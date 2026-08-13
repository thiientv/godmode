"""Small, dependency-free checks for the Godmode Agent Skills catalog."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlsplit


ALLOWED_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_BODY_LINES = 500
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
ROUTING_STOPWORDS = {
    "a",
    "an",
    "and",
    "change",
    "coding",
    "for",
    "help",
    "in",
    "it",
    "me",
    "new",
    "of",
    "or",
    "the",
    "this",
    "to",
    "use",
    "when",
    "with",
}


@dataclass(frozen=True)
class SkillRecord:
    """A discovered skill and its parsed frontmatter."""

    directory: Path
    metadata: dict[str, object]
    body: str

    @property
    def name(self) -> str:
        value = self.metadata.get("name")
        return value if isinstance(value, str) else ""

    @property
    def description(self) -> str:
        value = self.metadata.get("description")
        return value if isinstance(value, str) else ""


def _parse_scalar(value: str) -> object:
    """Parse the scalar subset used by this repository's frontmatter."""

    stripped = value.strip()
    if not stripped:
        return ""
    if stripped.startswith('"') and stripped.endswith('"'):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid quoted scalar: {error}") from error
    if stripped.startswith("'") and stripped.endswith("'"):
        return stripped[1:-1].replace("''", "'")
    if stripped in {"true", "false"}:
        return stripped == "true"
    if stripped in {"null", "~"}:
        return None
    if stripped.startswith("&") or stripped.startswith("*"):
        raise ValueError("YAML aliases are not allowed")
    return stripped


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Parse the small YAML frontmatter subset used by public skills.

    The validator intentionally has no runtime dependency on PyYAML. It accepts
    simple scalars, folded/literal descriptions, and a one-level metadata map,
    which covers the Agent Skills fields Godmode publishes.
    """

    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter (---)")

    closing_match = re.search(r"\n---(?:\n|$)", text[4:])
    if closing_match is None:
        raise ValueError("frontmatter is not closed with ---")

    header_end = 4 + closing_match.start()
    body_start = 4 + closing_match.end()
    header = text[4:header_end]
    body = text[body_start:]
    values: dict[str, object] = {}
    lines = header.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            raise ValueError(f"unexpected indented frontmatter line: {line!r}")
        if ":" not in line:
            raise ValueError(f"frontmatter line has no key/value separator: {line!r}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise ValueError("frontmatter contains an empty key")

        if raw_value in {">", ">-", ">+", "|", "|-", "|+"}:
            block_lines: list[str] = []
            while index < len(lines) and (lines[index].startswith(" ") or lines[index].startswith("\t")):
                block_lines.append(lines[index].strip())
                index += 1
            separator = "\n" if raw_value.startswith("|") else " "
            values[key] = separator.join(block_lines).strip()
            continue

        if raw_value == "":
            nested: dict[str, object] = {}
            while index < len(lines) and (lines[index].startswith(" ") or lines[index].startswith("\t")):
                nested_line = lines[index].strip()
                index += 1
                if ":" not in nested_line:
                    raise ValueError(f"invalid nested frontmatter line: {nested_line!r}")
                nested_key, nested_value = nested_line.split(":", 1)
                nested_key = nested_key.strip()
                if not nested_key:
                    raise ValueError("frontmatter contains an empty nested key")
                nested[nested_key] = _parse_scalar(nested_value)
            values[key] = nested
            continue

        values[key] = _parse_scalar(raw_value)

    return values, body


def discover_skills(root: Path) -> list[Path]:
    """Return direct public skill directories in deterministic order."""

    skills_root = root / "skills"
    if not skills_root.is_dir():
        return []
    return sorted(
        path.parent
        for path in skills_root.glob("*/SKILL.md")
        if path.is_file()
    )


def load_skill(skill_dir: Path) -> SkillRecord:
    """Load one skill from its canonical SKILL.md file."""

    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    return SkillRecord(skill_dir, metadata, body)


def _validate_local_links(record: SkillRecord) -> list[str]:
    errors: list[str] = []
    for raw_target in LINK_PATTERN.findall(record.body):
        target = raw_target.strip().strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith("#"):
            continue
        relative_target = unquote(parsed.path)
        if not relative_target:
            continue
        candidate = (record.directory / relative_target).resolve()
        skill_root = record.directory.resolve()
        if skill_root not in candidate.parents and candidate != skill_root:
            errors.append(f"local link escapes skill directory: {target}")
        elif not candidate.exists():
            errors.append(f"local link target does not exist: {target}")
    return errors


def _validate_agent_metadata(record: SkillRecord) -> list[str]:
    """Validate optional OpenAI skill UI metadata without a YAML dependency."""

    path = record.directory / "agents" / "openai.yaml"
    if not path.is_file():
        return []

    prefix = f"{record.directory.relative_to(record.directory.parents[1])}"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return [f"{prefix}: cannot read agents/openai.yaml: {error}"]
    if not lines or lines[0].strip() != "interface:":
        return [f"{prefix}: agents/openai.yaml must start with interface:"]

    interface: dict[str, object] = {}
    for line in lines[1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith("  ") or line.startswith("   ") or ":" not in line:
            return [f"{prefix}: agents/openai.yaml contains unsupported YAML structure"]
        key, raw_value = line.strip().split(":", 1)
        try:
            interface[key] = _parse_scalar(raw_value)
        except ValueError as error:
            return [f"{prefix}: agents/openai.yaml {error}"]

    errors: list[str] = []
    for field in ("display_name", "short_description", "default_prompt"):
        value = interface.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}: agents/openai.yaml interface.{field} must be a non-empty string")
    default_prompt = interface.get("default_prompt")
    invocation = f"${record.name}"
    if isinstance(default_prompt, str) and invocation not in default_prompt:
        errors.append(f"{prefix}: agents/openai.yaml default_prompt must mention {invocation}")
    if any(isinstance(value, str) and "[TODO" in value for value in interface.values()):
        errors.append(f"{prefix}: agents/openai.yaml contains unfinished TODO text")
    return errors


def validate_skill(record: SkillRecord) -> list[str]:
    """Validate one skill against the Agent Skills format and Godmode policy."""

    errors: list[str] = []
    metadata = record.metadata
    prefix = f"{record.directory.relative_to(record.directory.parents[1])}"

    unexpected = sorted(set(metadata) - ALLOWED_FRONTMATTER_FIELDS)
    if unexpected:
        errors.append(f"{prefix}: unexpected frontmatter fields: {', '.join(unexpected)}")

    name = metadata.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"{prefix}: name must be a non-empty string")
    else:
        if len(name) > MAX_NAME_LENGTH:
            errors.append(f"{prefix}: name exceeds {MAX_NAME_LENGTH} characters")
        if not NAME_PATTERN.fullmatch(name):
            errors.append(f"{prefix}: name must be lowercase kebab-case")
        if name != record.directory.name:
            errors.append(f"{prefix}: name does not match directory {record.directory.name!r}")

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{prefix}: description must be a non-empty string")
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"{prefix}: description exceeds {MAX_DESCRIPTION_LENGTH} characters")

    for field, max_length in (("compatibility", MAX_COMPATIBILITY_LENGTH),):
        value = metadata.get(field)
        if value is not None:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}: {field} must be a non-empty string")
            elif len(value) > max_length:
                errors.append(f"{prefix}: {field} exceeds {max_length} characters")

    license_value = metadata.get("license")
    if license_value is not None and not isinstance(license_value, str):
        errors.append(f"{prefix}: license must be a string")

    skill_metadata = metadata.get("metadata")
    if skill_metadata is not None:
        if not isinstance(skill_metadata, dict):
            errors.append(f"{prefix}: metadata must be a mapping")
        else:
            for key, value in skill_metadata.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append(f"{prefix}: metadata keys and values must be strings")

    body_lines = record.body.splitlines()
    if not any(line.strip() for line in body_lines):
        errors.append(f"{prefix}: skill body must not be empty")
    if len(body_lines) > MAX_BODY_LINES:
        errors.append(f"{prefix}: skill body exceeds {MAX_BODY_LINES} lines")

    errors.extend(f"{prefix}: {error}" for error in _validate_local_links(record))
    errors.extend(_validate_agent_metadata(record))
    return errors


def tokenize(text: str) -> set[str]:
    """Return routing terms while ignoring generic instruction words."""

    return {
        token
        for token in TOKEN_PATTERN.findall(text.lower().replace("-", " "))
        if token not in ROUTING_STOPWORDS
    }


def route_scores(records: Iterable[SkillRecord], prompt: str) -> list[tuple[str, float]]:
    """Rank skills with a small deterministic lexical routing proxy.

    Native clients remain the routing authority. This proxy only catches
    descriptions that omit their own trigger vocabulary or collide too much.
    """

    query_terms = tokenize(prompt)
    record_list = list(records)
    document_terms = {record.name: tokenize(record.description) for record in record_list}
    document_frequency = {
        term: sum(term in terms for terms in document_terms.values())
        for terms in document_terms.values()
        for term in terms
    }
    scored: list[tuple[str, float]] = []
    for record in record_list:
        terms = document_terms[record.name]
        score = 0.0
        for term in query_terms & terms:
            score += 1.0 / max(1, document_frequency[term])
        scored.append((record.name, score))
    return sorted(scored, key=lambda item: (-item[1], item[0]))


def validate_eval_file(path: Path, known_names: set[str]) -> list[str]:
    """Validate a deterministic routing-eval file."""

    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{path}: invalid JSON: {error}"]

    if not isinstance(payload, dict):
        return [f"{path}: eval must be a JSON object"]
    skill_name = payload.get("skill")
    if not isinstance(skill_name, str) or skill_name not in known_names:
        errors.append(f"{path}: skill must name a known skill")

    for kind, minimum in (("positive", 3), ("negative", 2)):
        cases = payload.get(kind)
        if not isinstance(cases, list) or len(cases) < minimum:
            errors.append(f"{path}: {kind} must contain at least {minimum} cases")
            continue
        for index, case in enumerate(cases):
            if not isinstance(case, dict) or not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                errors.append(f"{path}: {kind}[{index}] needs a non-empty prompt")
                continue
            if kind == "positive":
                top_k = case.get("top_k", 1)
                if not isinstance(top_k, int) or top_k < 1:
                    errors.append(f"{path}: positive[{index}].top_k must be a positive integer")
            else:
                owner = case.get("owner")
                if not isinstance(owner, str) or owner not in known_names or owner == skill_name:
                    errors.append(f"{path}: negative[{index}].owner must be another known skill")
    return errors


def validate_eval_routing(path: Path, payload: object, records: Iterable[SkillRecord]) -> list[str]:
    """Check that eval prompts route to the declared owner in the proxy."""

    if not isinstance(payload, dict):
        return [f"{path}: eval must be a JSON object"]
    skill_name = payload.get("skill")
    if not isinstance(skill_name, str):
        return [f"{path}: routing cannot run without a skill name"]

    record_list = list(records)
    known_names = {record.name for record in record_list}
    if skill_name not in known_names:
        return [f"{path}: routing references an unknown skill {skill_name!r}"]

    errors: list[str] = []
    for index, case in enumerate(payload.get("positive", [])):
        if not isinstance(case, dict) or not isinstance(case.get("prompt"), str):
            continue
        ranking = route_scores(record_list, case["prompt"])
        top_k = case.get("top_k", 1)
        ranked_names = [name for name, _ in ranking]
        if skill_name not in ranked_names[:top_k]:
            errors.append(
                f"{path}: positive[{index}] routes {ranked_names[:top_k]} instead of {skill_name}"
            )

    for index, case in enumerate(payload.get("negative", [])):
        if not isinstance(case, dict) or not isinstance(case.get("prompt"), str):
            continue
        owner = case.get("owner")
        if not isinstance(owner, str) or owner not in known_names:
            continue
        scores = dict(route_scores(record_list, case["prompt"]))
        if scores.get(owner, 0.0) <= scores.get(skill_name, 0.0):
            errors.append(
                f"{path}: negative[{index}] does not rank {owner} above {skill_name}"
            )
    return errors
