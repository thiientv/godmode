#!/usr/bin/env python3
"""Validate the Godmode skill catalog, links, and routing eval fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from skilllib import (
    discover_skills,
    load_skill,
    validate_eval_file,
    validate_eval_routing,
    validate_skill,
)
from behavior_eval import validate_cases


def validate_repository(root: Path, include_evals: bool = True) -> list[str]:
    """Return all validation errors without stopping at the first problem."""

    errors: list[str] = []
    errors.extend(validate_manifests(root))
    errors.extend(validate_versions(root))
    skill_dirs = discover_skills(root)
    if not skill_dirs:
        return ["skills/: no public SKILL.md files found"]

    records = []
    for skill_dir in skill_dirs:
        try:
            record = load_skill(skill_dir)
        except (OSError, ValueError) as error:
            errors.append(f"{skill_dir}: cannot load SKILL.md: {error}")
            continue
        records.append(record)
        errors.extend(validate_skill(record))

    names = [record.name for record in records]
    duplicates = sorted({name for name in names if names.count(name) > 1 and name})
    errors.extend(f"duplicate skill name: {name}" for name in duplicates)

    if include_evals:
        known_names = set(names)
        eval_dir = root / "evals"
        for record in records:
            eval_file = eval_dir / f"{record.name}.json"
            if not eval_file.is_file():
                errors.append(f"{eval_file}: missing routing eval file")
            else:
                errors.extend(validate_eval_file(eval_file, known_names))
                try:
                    payload = json.loads(eval_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    payload = None
                errors.extend(validate_eval_routing(eval_file, payload, records))

        if eval_dir.is_dir():
            expected = {f"{record.name}.json" for record in records}
            for eval_file in sorted(eval_dir.glob("*.json")):
                if eval_file.name not in expected:
                    errors.append(f"{eval_file}: eval does not correspond to a public skill")

        behavior_eval_dir = eval_dir / "behavior"
        if not behavior_eval_dir.is_dir():
            errors.append(f"{behavior_eval_dir}: behavior evaluation directory is missing")
        else:
            behavior_files = sorted(behavior_eval_dir.glob("*.json"))
            if not behavior_files:
                errors.append(f"{behavior_eval_dir}: no behavior case sets found")
            for behavior_file in behavior_files:
                try:
                    behavior_payload = json.loads(behavior_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as error:
                    errors.append(f"{behavior_file}: invalid JSON: {error}")
                    continue
                errors.extend(
                    f"{behavior_file}: {error}"
                    for error in validate_cases(behavior_payload)
                )

    return errors


def validate_manifests(root: Path) -> list[str]:
    """Validate the small set of distribution manifests without a client."""

    manifest_paths = [
        root / ".claude-plugin" / "plugin.json",
        root / ".claude-plugin" / "marketplace.json",
        root / ".codex-plugin" / "plugin.json",
        root / ".agents" / "plugins" / "marketplace.json",
        root / "hooks" / "hooks.json",
        root / "skills" / ".codex-plugin" / "plugin.json",
    ]
    errors: list[str] = []
    documents: dict[Path, object] = {}
    for path in manifest_paths:
        if not path.is_file():
            errors.append(f"{path}: required manifest is missing")
            continue
        try:
            documents[path] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path}: invalid JSON: {error}")

    semver_pattern = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
    for path in (manifest_paths[0], manifest_paths[2], manifest_paths[5]):
        document = documents.get(path)
        if not isinstance(document, dict):
            continue
        if document.get("name") != "godmode":
            errors.append(f"{path}: name must be godmode")
        version = document.get("version")
        if not isinstance(version, str) or semver_pattern.fullmatch(version) is None:
            errors.append(f"{path}: version must use semantic versioning")
        if not isinstance(document.get("description"), str) or not document["description"].strip():
            errors.append(f"{path}: description must be a non-empty string")
        author = document.get("author")
        if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
            errors.append(f"{path}: author.name must be a non-empty string")
        skills_path = document.get("skills")
        allowed_skills_paths = {"./", "."} if path == manifest_paths[5] else {"./skills", "./skills/"}
        if skills_path not in allowed_skills_paths:
            errors.append(f"{path}: skills path is invalid for this plugin root")
        if "hooks" in document:
            errors.append(f"{path}: unsupported hooks field must be omitted")
        if path in {manifest_paths[2], manifest_paths[5]}:
            interface = document.get("interface")
            required_interface_fields = (
                "displayName",
                "shortDescription",
                "longDescription",
                "developerName",
                "category",
                "capabilities",
            )
            if not isinstance(interface, dict):
                errors.append(f"{path}: interface must be an object")
            else:
                for field in required_interface_fields:
                    value = interface.get(field)
                    if field == "capabilities":
                        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                            errors.append(f"{path}: interface.capabilities must be a non-empty string list")
                    elif not isinstance(value, str) or not value.strip():
                        errors.append(f"{path}: interface.{field} must be a non-empty string")
                prompts = interface.get("defaultPrompt")
                if prompts is not None:
                    if not isinstance(prompts, list) or len(prompts) > 3:
                        errors.append(f"{path}: interface.defaultPrompt must contain at most three strings")
                    elif not all(isinstance(prompt, str) and 0 < len(prompt) <= 128 for prompt in prompts):
                        errors.append(f"{path}: interface.defaultPrompt entries must be 1-128 characters")

    source_codex = documents.get(manifest_paths[2])
    packaged_codex = documents.get(manifest_paths[5])
    if isinstance(source_codex, dict) and isinstance(packaged_codex, dict):
        for field in ("name", "version", "description", "author", "homepage", "repository", "license", "interface"):
            if source_codex.get(field) != packaged_codex.get(field):
                errors.append(f"{manifest_paths[5]}: {field} must match the root Codex manifest")

    claude_marketplace = documents.get(manifest_paths[1])
    if isinstance(claude_marketplace, dict):
        plugins = claude_marketplace.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1:
            errors.append(f"{manifest_paths[1]}: expected exactly one plugin")
        elif not isinstance(plugins[0], dict) or plugins[0].get("name") != "godmode" or plugins[0].get("source") != "./":
            errors.append(f"{manifest_paths[1]}: plugin must publish godmode from ./")

    codex_marketplace = documents.get(manifest_paths[3])
    if isinstance(codex_marketplace, dict):
        plugins = codex_marketplace.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1:
            errors.append(f"{manifest_paths[3]}: expected exactly one plugin")
        elif not isinstance(plugins[0], dict):
            errors.append(f"{manifest_paths[3]}: plugin entry must be an object")
        else:
            source = plugins[0].get("source")
            if not isinstance(source, dict) or source.get("path") != "./skills":
                errors.append(f"{manifest_paths[3]}: plugin must publish from ./skills")
            policy = plugins[0].get("policy")
            if not isinstance(policy, dict):
                errors.append(f"{manifest_paths[3]}: plugin policy must be an object")
            else:
                if policy.get("installation") not in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}:
                    errors.append(f"{manifest_paths[3]}: invalid installation policy")
                if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                    errors.append(f"{manifest_paths[3]}: invalid authentication policy")
            if not isinstance(plugins[0].get("category"), str) or not plugins[0]["category"].strip():
                errors.append(f"{manifest_paths[3]}: plugin category must be a non-empty string")

    return errors


def validate_versions(root: Path) -> list[str]:
    """Require release-bearing manifests to agree with package.json."""

    paths = [
        root / "package.json",
        root / ".claude-plugin" / "plugin.json",
        root / ".codex-plugin" / "plugin.json",
        root / "skills" / ".codex-plugin" / "plugin.json",
    ]
    errors: list[str] = []
    versions: dict[Path, str] = {}
    for path in paths:
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        version = payload.get("version") if isinstance(payload, dict) else None
        if not isinstance(version, str) or not version.strip():
            errors.append(f"{path}: version must be a non-empty string")
        else:
            versions[path] = version

    package_version = versions.get(paths[0])
    if package_version is not None:
        for path, version in versions.items():
            if version != package_version:
                errors.append(f"{path}: version {version!r} does not match package version {package_version!r}")

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    if marketplace_path.is_file() and package_version is not None:
        try:
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            marketplace = None
        if isinstance(marketplace, dict):
            metadata = marketplace.get("metadata")
            plugins = marketplace.get("plugins")
            metadata_version = metadata.get("version") if isinstance(metadata, dict) else None
            plugin_version = plugins[0].get("version") if isinstance(plugins, list) and plugins and isinstance(plugins[0], dict) else None
            if metadata_version != package_version:
                errors.append(f"{marketplace_path}: metadata version does not match package version")
            if plugin_version != package_version:
                errors.append(f"{marketplace_path}: plugin version does not match package version")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-evals", action="store_true", help="skip eval fixture validation")
    args = parser.parse_args(argv)

    errors = validate_repository(args.root.resolve(), include_evals=not args.skip_evals)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    skill_count = len(discover_skills(args.root.resolve()))
    print(f"Validated {skill_count} public skills, local links, and routing evals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
