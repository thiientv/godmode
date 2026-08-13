#!/usr/bin/env python3
"""Run conservative, dependency-free static UI checks on source files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


EXTENSIONS = {
    ".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".css", ".scss", ".sass", ".less"
}
EXCLUDED_DIRECTORIES = {".git", ".next", "build", "coverage", "dist", "examples", "node_modules"}
MARKUP_EXTENSIONS = {".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}
STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    message: str
    evidence: str


def source_files(target: Path) -> list[Path]:
    """Return supported source files below a file or directory."""

    if target.is_file():
        return [target] if target.suffix.lower() in EXTENSIONS else []
    if not target.is_dir():
        return []
    return sorted(
        path
        for path in target.rglob("*")
        if path.is_file()
        and path.suffix.lower() in EXTENSIONS
        and not EXCLUDED_DIRECTORIES.intersection(path.relative_to(target).parts[:-1])
    )


def line_number(text: str, offset: int) -> int:
    """Return a one-based line number for a string offset."""

    return text.count("\n", 0, offset) + 1


def is_primary_surface(path: Path) -> bool:
    """Return whether a file is expected to own a page-level heading."""

    if path.suffix.lower() in {".html", ".htm"}:
        return True
    return path.stem.lower() in {"app", "home", "index", "page", "route"}


def findings_for_file(path: Path, root: Path) -> list[Finding]:
    """Apply conservative checks to one source file."""

    text = path.read_text(encoding="utf-8", errors="replace")
    relative = str(path.relative_to(root)) if path != root else path.name
    findings: list[Finding] = []

    def add(rule: str, severity: str, offset: int, message: str, evidence: str) -> None:
        findings.append(Finding(rule, severity, relative, line_number(text, offset), message, evidence))

    if path.suffix.lower() in MARKUP_EXTENSIONS:
        if path.suffix.lower() in {".html", ".htm"}:
            viewport = re.search(r"<meta\b[^>]*name\s*=\s*['\"]viewport['\"][^>]*>", text, re.IGNORECASE)
            if viewport is None:
                add("viewport-meta", "P1", 0, "Document has no viewport meta declaration for responsive layout.", "<meta name=\"viewport\">")
            elif re.search(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1(?:\.0+)?(?:\D|$)", viewport.group(0), re.IGNORECASE):
                add("zoom-disabled", "P1", viewport.start(), "Viewport configuration may prevent user zoom.", viewport.group(0)[:160])

        if is_primary_surface(path) and not re.search(r"<h1\b", text, re.IGNORECASE):
            add("missing-primary-heading", "P1", 0, "No h1-like primary heading was found in this file.", "<h1>")

        for match in re.finditer(r"<img\b[^>]*>", text, re.IGNORECASE):
            tag = match.group(0)
            if not re.search(r"\balt\s*=", tag, re.IGNORECASE):
                add("image-alt", "P1", match.start(), "Image has no explicit alt attribute.", tag[:160])
            if not (re.search(r"\bwidth\s*=", tag, re.IGNORECASE) and re.search(r"\bheight\s*=", tag, re.IGNORECASE)):
                add("image-dimensions", "P2", match.start(), "Image has no explicit width and height; verify layout space is reserved.", tag[:160])

        label_targets = set(re.findall(r"<label\b[^>]*\bfor\s*=\s*['\"]([^'\"]+)", text, re.IGNORECASE))
        label_targets.update(re.findall(r"<label\b[^>]*\bhtmlFor\s*=\s*['\"]([^'\"]+)", text))
        for match in re.finditer(r"<(input|select|textarea)\b([^>]*)>", text, re.IGNORECASE):
            tag_name, attributes = match.groups()
            if tag_name.lower() == "input" and re.search(r"\btype\s*=\s*['\"]hidden['\"]", attributes, re.IGNORECASE):
                continue
            has_direct_name = bool(re.search(r"\baria-label(?:ledby)?\s*=\s*['\"]\s*[^'\"]+|\btitle\s*=\s*['\"]\s*[^'\"]+", attributes, re.IGNORECASE))
            identifier = re.search(r"\bid\s*=\s*['\"]([^'\"]+)", attributes, re.IGNORECASE)
            if not has_direct_name and (identifier is None or identifier.group(1) not in label_targets):
                add("form-control-name", "P1", match.start(), f"{tag_name} may have no associated visible or accessible label.", match.group(0)[:160])

        for match in re.finditer(r"<(button|a)\b([^>]*)>", text, re.IGNORECASE):
            tag_name, attributes = match.groups()
            following = text[match.end():]
            closing = re.search(r"</(?:button|a)>", following, re.IGNORECASE)
            content = following[:closing.start()] if closing else ""
            visible_text = re.sub(r"<[^>]+>", " ", content)
            has_name = bool(
                re.search(r"\baria-label\s*=\s*['\"]\s*[^'\"]+|\btitle\s*=\s*['\"]\s*[^'\"]+", attributes, re.IGNORECASE)
                or visible_text.strip()
            )
            if not has_name:
                add("control-name", "P1", match.start(), f"{tag_name} may have no accessible name.", match.group(0)[:160])

        for match in re.finditer(r"\bonclick\s*=|\bonClick\s*=", text):
            nearby = text[max(0, match.start() - 120):match.start() + 160]
            if not re.search(r"\bbutton\b|\brole\s*=\s*[\"']button", nearby, re.IGNORECASE):
                add("non-semantic-action", "P1", match.start(), "Click handler may be attached to a non-semantic element.", nearby)

        for match in re.finditer(r"\btabindex\s*=\s*['\"]?([1-9]\d*)|\btabIndex\s*=\s*\{?([1-9]\d*)", text):
            add("positive-tabindex", "P1", match.start(), "Positive tabindex creates a fragile keyboard order.", match.group(0))

        for match in re.finditer(r"<(?:div|span)\b([^>]*)\brole\s*=\s*['\"]button['\"]([^>]*)>", text, re.IGNORECASE):
            attributes = " ".join(match.groups())
            if not re.search(r"\btabindex\s*=|\btabIndex\s*=", attributes):
                add("role-button-keyboard", "P1", match.start(), "Custom role=button may not be keyboard focusable; prefer a native button.", match.group(0)[:160])

        for match in re.finditer(r"\bautoFocus\b|\bautofocus\b", text):
            add("autofocus", "P2", match.start(), "Automatic focus can disorient users; verify it is necessary and announced by context.", match.group(0))

    if path.suffix.lower() in STYLE_EXTENSIONS:
        for match in re.finditer(r"outline\s*:\s*none|outline\s*:\s*0", text, re.IGNORECASE):
            add("focus-outline", "P1", match.start(), "Focus outline is removed; verify an equivalent visible focus style.", match.group(0))
        for match in re.finditer(r"transition\s*:\s*all\b", text, re.IGNORECASE):
            add("transition-all", "P2", match.start(), "transition: all can animate unintended properties and create fragile motion.", match.group(0))
        for match in re.finditer(r"overflow-x\s*:\s*hidden", text, re.IGNORECASE):
            add("hidden-overflow", "P2", match.start(), "Horizontal overflow is hidden; verify clipped content is not masking a responsive defect.", match.group(0))
        for match in re.finditer(r"(?:width|min-width|max-width)\s*:\s*100vw", text, re.IGNORECASE):
            add("viewport-width-overflow", "P2", match.start(), "100vw can include scrollbar width and create horizontal overflow.", match.group(0))
        has_animation = bool(re.search(r"\banimation(?:-name)?\s*:", text, re.IGNORECASE))
        has_reduced_motion = bool(re.search(r"prefers-reduced-motion", text, re.IGNORECASE))
        if has_animation and not has_reduced_motion:
            match = re.search(r"\banimation(?:-name)?\s*:", text, re.IGNORECASE)
            if match is not None:
                add("reduced-motion", "P1", match.start(), "Animation is present without an in-file reduced-motion override; verify one exists in the owning style layer.", match.group(0))

    return findings


def audit(target: Path) -> list[Finding]:
    """Audit all supported files under a target."""

    files = source_files(target)
    root = target if target.is_dir() else target.parent
    findings: list[Finding] = []
    for path in files:
        findings.extend(findings_for_file(path, root))
    return findings


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="HTML/CSS/UI source file or directory.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("none", "P0", "P1", "P2", "P3"), default="none")
    parser.add_argument("--allow-empty", action="store_true", help="treat zero supported source files as a successful audit")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the audit and return a useful CI status."""

    args = parse_args(argv)
    target = args.target.resolve()
    if not target.exists():
        print(f"Target does not exist: {args.target}")
        return 2
    files = source_files(target)
    findings = audit(target)
    if not files and not args.allow_empty:
        if args.format == "json":
            print(json.dumps({"status": "inconclusive", "files_checked": 0, "findings": []}, indent=2))
        else:
            print("Audit is inconclusive: no supported UI source files were found.")
        return 2

    status = "findings" if findings else "clean"
    if args.format == "json":
        print(
            json.dumps(
                {
                    "status": status,
                    "files_checked": len(files),
                    "findings": [asdict(finding) for finding in findings],
                },
                indent=2,
            )
        )
    else:
        for finding in findings:
            print(f"[{finding.severity}] {finding.rule} {finding.path}:{finding.line} — {finding.message}")
        print(f"Checked {len(files)} source file(s); found {len(findings)} finding(s).")

    if args.fail_on == "none":
        return 0
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return 1 if any(order[finding.severity] <= order[args.fail_on] for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
