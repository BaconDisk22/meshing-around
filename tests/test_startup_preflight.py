import pathlib
import tempfile
import unittest
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
from startup_preflight import check_paths

class PreflightTests(unittest.TestCase):
    def test_missing_config_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            bot = root / "mesh_bot.py"
            bot.write_text("pass")
            with self.assertRaisesRegex(FileNotFoundError, "Radio configuration"):
                check_paths(root, bot)
            (root / "config.ini").write_text("[interface]")
            check_paths(root, bot)

if __name__ == "__main__":
    unittest.main()
