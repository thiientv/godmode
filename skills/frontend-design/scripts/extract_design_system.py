#!/usr/bin/env python3
"""Extract conservative design-system evidence from frontend source files."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Iterable, Sequence


EXTENSIONS = {
    ".css", ".scss", ".sass", ".less", ".html", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"
}
EXCLUDED_DIRECTORIES = {".git", ".next", "build", "coverage", "dist", "examples", "node_modules"}
VARIABLE_PATTERN = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;}{]+)")
HEX_PATTERN = re.compile(r"(?<![\w-])#[0-9a-fA-F]{3,8}\b")
FONT_PATTERN = re.compile(r"font-family\s*:\s*([^;}{]+)", re.IGNORECASE)
LENGTH_PATTERN = re.compile(r"(?<![\w.-])(-?\d+(?:\.\d+)?(?:px|rem|em))(?![\w-])")
RADIUS_PATTERN = re.compile(r"border-radius\s*:\s*([^;}{]+)", re.IGNORECASE)
MEDIA_PATTERN = re.compile(r"@media\s*([^\{]+)", re.IGNORECASE)


def source_files(target: Path) -> list[Path]:
    """Return supported frontend files below a target."""

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


def most_common(values: Iterable[str], limit: int = 20) -> list[dict[str, object]]:
    """Return stable frequency records."""

    return [{"value": value, "count": count} for value, count in Counter(values).most_common(limit)]


def detect_stacks(files: Iterable[Path], target: Path) -> list[str]:
    """Infer likely UI stacks only from file extensions and names."""

    paths = list(files)
    suffixes = {path.suffix.lower() for path in paths}
    stacks: list[str] = []
    if suffixes.intersection({".jsx", ".tsx"}):
        stacks.append("react-or-jsx")
    if ".vue" in suffixes:
        stacks.append("vue")
    if ".svelte" in suffixes:
        stacks.append("svelte")
    config_root = target if target.is_dir() else target.parent
    if any((config_root / name).is_file() for name in ("tailwind.config.js", "tailwind.config.ts", "tailwind.config.mjs")):
        stacks.append("tailwind")
    if suffixes.intersection({".css", ".scss", ".sass", ".less"}):
        stacks.append("css")
    return stacks


def line_number(text: str, offset: int) -> int:
    """Return a one-based line number for an offset."""

    return text.count("\n", 0, offset) + 1


def extract(target: Path) -> dict[str, object]:
    """Extract lexical token and layout evidence without assigning semantics."""

    files = source_files(target)
    variables: dict[str, set[str]] = {}
    variable_occurrences: dict[str, list[dict[str, object]]] = {}
    colors: list[str] = []
    fonts: list[str] = []
    lengths: list[str] = []
    radii: list[str] = []
    media_queries: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        root = target if target.is_dir() else target.parent
        relative_path = str(path.relative_to(root))
        for match in VARIABLE_PATTERN.finditer(text):
            name, value = match.groups()
            variables.setdefault(name, set()).add(value.strip())
            variable_occurrences.setdefault(name, []).append(
                {"path": relative_path, "line": line_number(text, match.start())}
            )
        colors.extend(value.lower() for value in HEX_PATTERN.findall(text))
        fonts.extend(value.strip() for value in FONT_PATTERN.findall(text))
        lengths.extend(LENGTH_PATTERN.findall(text))
        radii.extend(value.strip() for value in RADIUS_PATTERN.findall(text))
        media_queries.extend(value.strip() for value in MEDIA_PATTERN.findall(text))

    return {
        "target": str(target),
        "files_checked": len(files),
        "detected_stacks": detect_stacks(files, target),
        "css_variables": [
            {
                "name": name,
                "values": sorted(values),
                "occurrences": variable_occurrences.get(name, []),
            }
            for name, values in sorted(variables.items())
        ],
        "frequent_colors": most_common(colors),
        "font_families": most_common(fonts),
        "frequent_lengths": most_common(lengths),
        "border_radii": most_common(radii),
        "media_queries": most_common(media_queries),
        "limits": [
            "Lexical extraction cannot infer semantic token intent.",
            "Utility classes and runtime-computed styles may require framework-specific inspection.",
            "Rendered verification is required before changing the design system.",
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Frontend source file or directory.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    return parser.parse_args(argv)


def render_markdown(report: dict[str, object]) -> str:
    """Render a compact human-readable extraction report."""

    lines = [
        "# Extracted design-system evidence",
        "",
        f"- Target: {report['target']}",
        f"- Files checked: {report['files_checked']}",
        f"- Detected stacks: {', '.join(report['detected_stacks']) or 'unknown'}",
        "",
        "## CSS variables",
    ]
    variables = report["css_variables"]
    if isinstance(variables, list) and variables:
        for item in variables:
            if isinstance(item, dict):
                occurrences = item.get("occurrences", [])
                first = occurrences[0] if isinstance(occurrences, list) and occurrences else None
                location = f" — {first['path']}:{first['line']}" if isinstance(first, dict) else ""
                lines.append(f"- `{item['name']}`: {', '.join(item['values'])}{location}")
    else:
        lines.append("- None found.")

    for key, title in (
        ("frequent_colors", "Frequent colors"),
        ("font_families", "Font families"),
        ("frequent_lengths", "Frequent lengths"),
        ("border_radii", "Border radii"),
        ("media_queries", "Media queries"),
    ):
        lines.extend(("", f"## {title}"))
        records = report[key]
        if isinstance(records, list) and records:
            for record in records[:10]:
                if isinstance(record, dict):
                    lines.append(f"- `{record['value']}` ({record['count']})")
        else:
            lines.append("- None found.")

    lines.extend(("", "## Limits"))
    limits = report["limits"]
    if isinstance(limits, list):
        lines.extend(f"- {limit}" for limit in limits)
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    """Run extraction and print the selected format."""

    args = parse_args(argv)
    target = args.target.resolve()
    if not target.exists():
        print(f"Target does not exist: {args.target}")
        return 2
    report = extract(target)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
