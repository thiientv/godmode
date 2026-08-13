from __future__ import annotations

from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontend-design" / "scripts"))
from design_catalog import search_entries  # noqa: E402
from design_system import build_brief, render_markdown  # noqa: E402
from extract_design_system import extract  # noqa: E402

sys.path.insert(0, str(ROOT / "skills" / "ui-ux-review" / "scripts"))
from audit_ui import audit, main as audit_main  # noqa: E402


class UiHelperTests(unittest.TestCase):
    def test_design_brief_is_deterministic_and_stack_aware(self) -> None:
        first = build_brief("analytics dashboard", "technical", "react", "dense")
        second = build_brief("analytics dashboard", "technical", "react", "dense")
        self.assertEqual(first, second)
        self.assertEqual(first.display_font, "Space Grotesk")
        self.assertEqual(first.density, "dense")
        self.assertEqual(first.style, "technical")
        self.assertEqual(first.palette, "navy-and-sky")
        self.assertEqual(first.accent, "#2F6FED")
        self.assertEqual(first.surface, "#F4F7FB")
        self.assertTrue(search_entries("dashboard async loading", domain="ux"))
        self.assertTrue(search_entries("keyboard focus dialog", domain="accessibility"))
        self.assertTrue(search_entries("operations dashboard workspace", domain="layout"))
        self.assertIn("semantic", render_markdown(first))

    def test_design_brief_normalizes_stack_and_rejects_unknown_style(self) -> None:
        brief = build_brief("developer dashboard", "technical", "next", "standard")
        self.assertEqual(brief.stack, "nextjs")
        self.assertEqual(search_entries("dashboard", domain="style", limit=0), [])
        with self.assertRaisesRegex(ValueError, "Unknown catalog style"):
            build_brief("developer dashboard", "technical", "react", "standard", "brutalist")

    def test_design_system_extraction_reports_tokens_and_repetition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "theme.css").write_text(
                ":root { --surface: #f7f5f0; --radius: 8px; }\n"
                ".card { color: #1a1a1a; border-radius: 8px; padding: 16px; }\n"
                "@media (min-width: 48rem) { .card { padding: 24px; } }\n",
                encoding="utf-8",
            )
            report = extract(root)
        self.assertEqual(report["files_checked"], 1)
        self.assertIn("css", report["detected_stacks"])
        self.assertEqual(report["css_variables"][0]["name"], "--radius")
        self.assertEqual(report["css_variables"][0]["occurrences"][0]["path"], "theme.css")
        self.assertTrue(any(item["value"] == "8px" for item in report["frequent_lengths"]))

    def test_design_system_extraction_includes_typescript_and_skips_generated_trees(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "theme.ts").write_text("const theme = `:root { --accent: #123456; }`;\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "vendor.css").write_text(":root { --vendor: #fff; }\n", encoding="utf-8")
            report = extract(root)
        self.assertEqual(report["files_checked"], 1)
        self.assertEqual([item["name"] for item in report["css_variables"]], ["--accent"])

    def test_ui_audit_reports_concrete_static_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "index.html").write_text(
                "<main><img src='hero.png'><input id='email'><div onclick='openMenu()'>Menu</div></main>",
                encoding="utf-8",
            )
            (root / "styles.css").write_text(
                ".button { outline: none; transition: all 200ms; overflow-x: hidden; width: 100vw; animation: pulse 1s; }\n",
                encoding="utf-8",
            )
            rules = {finding.rule for finding in audit(root)}
        self.assertIn("missing-primary-heading", rules)
        self.assertIn("image-alt", rules)
        self.assertIn("non-semantic-action", rules)
        self.assertIn("focus-outline", rules)
        self.assertIn("transition-all", rules)
        self.assertIn("hidden-overflow", rules)
        self.assertIn("viewport-meta", rules)
        self.assertIn("image-dimensions", rules)
        self.assertIn("form-control-name", rules)
        self.assertIn("viewport-width-overflow", rules)
        self.assertIn("reduced-motion", rules)

    def test_ui_audit_does_not_require_h1_in_leaf_component(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "Button.tsx").write_text("export const Button = () => <button>Save</button>;\n", encoding="utf-8")
            rules = {finding.rule for finding in audit(root)}
        self.assertNotIn("missing-primary-heading", rules)

    def test_ui_audit_reports_empty_scope_as_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output = io.StringIO()
            with redirect_stdout(output):
                status = audit_main([str(root), "--format", "json"])
            self.assertEqual(status, 2)
            self.assertIn('"status": "inconclusive"', output.getvalue())

            with redirect_stdout(io.StringIO()):
                allowed_status = audit_main([str(root), "--allow-empty"])
            self.assertEqual(allowed_status, 0)


if __name__ == "__main__":
    unittest.main()
