"""Static packaging checks that can run on CI without an Intel Mac."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PackagingContract(unittest.TestCase):
    def test_desktop_entrypoint_present(self):
        launcher = ROOT / "desktop" / "launcher.py"
        self.assertTrue(launcher.is_file())
        self.assertIn('if __name__ == "__main__":', launcher.read_text())

    def test_bot_entrypoint_present(self):
        self.assertTrue((ROOT / "mesh_bot.py").is_file())

if __name__ == "__main__":
    unittest.main()
