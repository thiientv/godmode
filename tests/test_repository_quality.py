from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from catalog import validate_catalog  # noqa: E402
from catalog_health import build_health_report  # noqa: E402
from compatibility import validate_compatibility, write_compatibility  # noqa: E402
from release_smoke import validate_archive  # noqa: E402
from repository_security import validate_public_files, validate_workflows  # noqa: E402


def _repository_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]


def _build_archive(path: Path) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for source in _repository_files():
            if source.is_file():
                archive.add(source, arcname=f"godmode-test/{source.relative_to(ROOT).as_posix()}")


class RepositoryQualityTests(unittest.TestCase):
    def test_current_catalog_and_compatibility_evidence_are_synchronized(self) -> None:
        self.assertEqual(validate_catalog(ROOT), [])
        self.assertEqual(validate_compatibility(ROOT), [])

    def test_catalog_check_reports_documentation_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "skills" / "sample-skill").mkdir(parents=True)
            (root / "evals").mkdir()
            (root / "docs").mkdir()
            (root / "skills" / "sample-skill" / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: Sample routing boundary.\n---\n# Sample\n",
                encoding="utf-8",
            )
            (root / "evals" / "sample-skill.json").write_text("{}", encoding="utf-8")
            (root / "catalog.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "groups": [
                            {"id": "workflow", "label": "Workflow", "skills": ["sample-skill"]}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "| Skill | Use |\n| --- | --- |\n| `sample-skill` | Sample |\n",
                encoding="utf-8",
            )
            (root / "README.zh-CN.md").write_text(
                "| Skill | Use |\n| --- | --- |\n| `sample-skill` | Sample |\n",
                encoding="utf-8",
            )
            (root / "docs" / "catalog.md").write_text("`sample-skill`\n", encoding="utf-8")
            self.assertEqual(validate_catalog(root), [])
            (root / "README.zh-CN.md").write_text("# Missing\n", encoding="utf-8")
            errors = validate_catalog(root)
        self.assertTrue(any("README.zh-CN.md: missing skills: sample-skill" in error for error in errors))

    def test_public_file_scan_rejects_hidden_unicode_and_personal_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            path = root / "unsafe.md"
            personal_path = "/" + "Users" + "/alice/private"
            path.write_text(f"safe\u202Etext\n{personal_path}\n", encoding="utf-8")
            errors = validate_public_files(root, [path])
        self.assertTrue(any("U+202E" in error for error in errors))
        self.assertTrue(any("personal home path" in error for error in errors))

    def test_public_file_scan_rejects_symlink_without_reading_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            target = root / "outside.txt"
            target.write_text("\u202Ehidden", encoding="utf-8")
            link = root / "published.md"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            errors = validate_public_files(root, [link])
        self.assertEqual(errors, ["published.md: symbolic links are not allowed in public files"])

    def test_workflow_scan_rejects_mutable_actions_and_checkout_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "unsafe.yml").write_text(
                "name: Unsafe\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - uses: actions/checkout@v7\n",
                encoding="utf-8",
            )
            errors = validate_workflows(root)
        self.assertTrue(any("full commit SHA" in error for error in errors))
        self.assertTrue(any("persist-credentials: false" in error for error in errors))

    def test_workflow_scan_accepts_pinned_read_only_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "safe.yml").write_text(
                "name: Safe\non: push\npermissions:\n  contents: read\njobs:\n  test:\n"
                "    runs-on: ubuntu-latest\n    steps:\n"
                "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
                "        with:\n          persist-credentials: false\n",
                encoding="utf-8",
            )
            errors = validate_workflows(root)
        self.assertEqual(errors, [])

    def test_compatibility_writer_updates_only_the_generated_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "compatibility").mkdir()
            (root / "docs").mkdir()
            evidence = {
                "schema_version": 1,
                "surfaces": [
                    {
                        "id": "sample",
                        "surface": "Sample client",
                        "evidence": "Recorded trace",
                        "status": "Verified",
                        "observed_at": "2026-08-13",
                        "client_version": "1.0.0",
                        "limitations": [],
                    }
                ],
            }
            (root / "compatibility" / "evidence.json").write_text(
                json.dumps(evidence), encoding="utf-8"
            )
            (root / "docs" / "compatibility.md").write_text(
                "Before\n<!-- compatibility-table:start -->\nstale\n"
                "<!-- compatibility-table:end -->\nAfter\n",
                encoding="utf-8",
            )
            self.assertEqual(write_compatibility(root), [])
            self.assertEqual(validate_compatibility(root), [])
            rendered = (root / "docs" / "compatibility.md").read_text(encoding="utf-8")
        self.assertIn("| Sample client | Recorded trace | Verified |", rendered)
        self.assertTrue(rendered.startswith("Before\n"))
        self.assertTrue(rendered.endswith("After\n"))

    def test_catalog_health_reports_real_resources(self) -> None:
        report = build_health_report(ROOT)
        skills = {item["name"]: item for item in report["skills"]}
        self.assertEqual(report["skill_count"], len(skills))
        self.assertEqual(skills["frontend-design"]["scripts"], 3)
        self.assertTrue(skills["codebase-orientation"]["has_routing_eval"])

    def test_code_tour_helper_validates_anchors_and_writes_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "src").mkdir()
            (root / "src" / "entry.py").write_text("first\nsecond\n", encoding="utf-8")
            spec = root / "tour.json"
            output = root / "request.tour"
            spec.write_text(
                json.dumps(
                    {
                        "title": "Request path",
                        "steps": [
                            {
                                "file": "src/entry.py",
                                "line": 2,
                                "description": "Continue through the entry point.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "skills" / "codebase-orientation" / "scripts" / "create_code_tour.py"),
                    str(spec),
                    str(output),
                    "--root",
                    str(root),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["$schema"], "https://aka.ms/codetour-schema")
        self.assertEqual(payload["steps"][0]["line"], 2)

    def test_release_archive_passes_full_extracted_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            archive = Path(temporary_directory) / "godmode-test.tar.gz"
            _build_archive(archive)
            errors = validate_archive(archive)
        self.assertEqual(errors, [])

    def test_release_archive_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            archive_path = Path(temporary_directory) / "unsafe.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                content = b"unsafe"
                info = tarfile.TarInfo("godmode/../escape.txt")
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
            errors = validate_archive(archive_path)
        self.assertTrue(any("unsafe path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
