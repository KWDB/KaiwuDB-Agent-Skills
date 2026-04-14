import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from init_skill import init_skill  # noqa: E402
from quick_validate import validate_skill  # noqa: E402


class ValidateSkillTests(unittest.TestCase):
    def make_skill(self, root: Path, content: str) -> Path:
        skill_dir = root / "demo-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent(content).strip() + "\n")
        return skill_dir

    def test_accepts_minimal_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.make_skill(
                Path(tmp),
                """
                ---
                name: demo-skill
                description: Use when users need help creating or refining a skill.
                ---

                # Demo Skill
                """,
            )

            valid, message = validate_skill(skill_dir)

        self.assertTrue(valid, message)

    def test_rejects_extra_frontmatter_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.make_skill(
                Path(tmp),
                """
                ---
                name: demo-skill
                description: Use when users need help creating or refining a skill.
                license: Example
                ---

                # Demo Skill
                """,
            )

            valid, message = validate_skill(skill_dir)

        self.assertFalse(valid)
        self.assertIn("Allowed properties are: description, name", message)

    def test_rejects_descriptions_without_trigger_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.make_skill(
                Path(tmp),
                """
                ---
                name: demo-skill
                description: Guide for creating effective skills.
                ---

                # Demo Skill
                """,
            )

            valid, message = validate_skill(skill_dir)

        self.assertFalse(valid)
        self.assertIn("start with 'Use when'", message)


class InitSkillTests(unittest.TestCase):
    def test_init_skill_creates_lean_design_first_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = init_skill("demo-skill", tmp)

            self.assertIsNotNone(skill_dir)
            skill_dir = Path(skill_dir)

            self.assertTrue((skill_dir / "SKILL.md").exists())
            self.assertTrue((skill_dir / "references" / "activation-design.md").exists())
            self.assertTrue((skill_dir / "references" / "domain-notes.md").exists())
            self.assertFalse((skill_dir / "scripts").exists())
            self.assertFalse((skill_dir / "assets").exists())


if __name__ == "__main__":
    unittest.main()
