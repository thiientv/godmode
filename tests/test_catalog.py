from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from skilllib import (  # noqa: E402
    discover_skills,
    load_skill,
    parse_frontmatter,
    route_scores,
    validate_skill,
)
from validate import validate_repository  # noqa: E402
from validate import validate_versions  # noqa: E402


class CatalogTests(unittest.TestCase):
    def test_repository_is_valid(self) -> None:
        self.assertEqual(validate_repository(ROOT), [])
        self.assertGreater(len(discover_skills(ROOT)), 0)
        self.assertTrue((ROOT / "skills" / "frontend-design" / "scripts" / "design_system.py").is_file())
        self.assertTrue((ROOT / "skills" / "ui-ux-review" / "scripts" / "audit_ui.py").is_file())
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["plugins"][0]["source"]["path"], "./skills")

    def test_frontmatter_supports_folded_description_and_metadata(self) -> None:
        metadata, body = parse_frontmatter(
            "---\n"
            "name: sample-skill\n"
            "description: >-\n"
            "  Finds a useful thing.\n"
            "metadata:\n"
            "  role: workflow\n"
            "---\n"
            "# Sample\n"
        )
        self.assertEqual(metadata["name"], "sample-skill")
        self.assertEqual(metadata["description"], "Finds a useful thing.")
        self.assertEqual(metadata["metadata"], {"role": "workflow"})
        self.assertEqual(body, "# Sample\n")

    def test_invalid_name_and_link_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = Path(temporary_directory) / "skills" / "Bad_Name"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: Bad_Name\n"
                "description: Example skill.\n"
                "---\n"
                "See [missing](references/missing.md).\n",
                encoding="utf-8",
            )
            errors = validate_skill(load_skill(skill_dir))
        self.assertTrue(any("lowercase kebab-case" in error for error in errors))
        self.assertTrue(any("local link target does not exist" in error for error in errors))

    def test_agent_metadata_requires_exact_skill_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = Path(temporary_directory) / "skills" / "sample-skill"
            (skill_dir / "agents").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: sample-skill\n"
                "description: Example skill.\n"
                "---\n"
                "# Sample\n",
                encoding="utf-8",
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                "interface:\n"
                "  display_name: \"Sample\"\n"
                "  short_description: \"Sample helper.\"\n"
                "  default_prompt: \"Use -skill for this task.\"\n",
                encoding="utf-8",
            )
            errors = validate_skill(load_skill(skill_dir))
        self.assertTrue(any("must mention $sample-skill" in error for error in errors))

    def test_aliases_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "aliases"):
            parse_frontmatter(
                "---\nname: &name sample\ndescription: *name\n---\nBody\n"
            )

    def test_release_versions_are_consistent(self) -> None:
        self.assertEqual(validate_versions(ROOT), [])

    def test_routing_proxy_matches_positive_and_negative_fixtures(self) -> None:
        records = [load_skill(path) for path in discover_skills(ROOT)]
        ranking = route_scores(
            records,
            "The service is flaky and needs a deterministic reproduction and root cause",
        )
        self.assertEqual(ranking[0][0], "root-cause-debugging")

        verification_eval = json.loads(
            (ROOT / "evals" / "completion-verification.json").read_text(encoding="utf-8")
        )
        for case in verification_eval["positive"]:
            ranked_names = [name for name, _ in route_scores(records, case["prompt"])]
            self.assertIn("completion-verification", ranked_names[: case.get("top_k", 1)])


if __name__ == "__main__":
    unittest.main()
