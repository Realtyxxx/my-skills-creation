import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillDocumentationTests(unittest.TestCase):
    def test_mode_documents_exist(self):
        modes_dir = ROOT / "modes"
        expected = {"ptx.md", "sass.md", "cubin.md", "fatbin.md"}

        self.assertTrue(modes_dir.is_dir())
        self.assertEqual({path.name for path in modes_dir.glob("*.md")}, expected)

    def test_architecture_documents_exist(self):
        arch_dir = ROOT / "arch"
        expected = {
            "volta.md",
            "turing.md",
            "ampere.md",
            "ada.md",
            "hopper.md",
            "blackwell.md",
        }

        self.assertTrue(arch_dir.is_dir())
        self.assertEqual({path.name for path in arch_dir.glob("*.md")}, expected)

    def test_skill_routes_to_mode_and_arch_documents(self):
        content = (ROOT / "SKILL.md").read_text()

        self.assertIn("modes/", content)
        self.assertIn("arch/", content)
        self.assertIn("references/nvcc_options.md", content)
        self.assertIn("references/architectures.md", content)
        self.assertIn("Load exactly one mode reference", content)
        self.assertIn("Load one architecture reference only when", content)

    def test_skill_keeps_mode_details_out_of_top_level_document(self):
        content = (ROOT / "SKILL.md").read_text()

        self.assertNotIn("Generate PTX for a kernel", content)
        self.assertNotIn("Generate SASS assembly", content)
        self.assertNotIn("Multi-architecture compilation", content)
        self.assertNotIn("SM 70, 72 (Volta)", content)


if __name__ == "__main__":
    _ = unittest.main()
