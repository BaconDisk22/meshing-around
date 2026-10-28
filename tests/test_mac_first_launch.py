"""Mac bundle initialization tests; no GUI or hardware required."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
from mac_app import prepare_workspace


class MacFirstLaunchTests(unittest.TestCase):
    def test_creates_config_without_overwriting_existing_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            bundle = root / "bundle"
            payload = bundle / "payload"
            payload.mkdir(parents=True)
            (payload / "config.template").write_text("[interface]\ntype = tcp\n")
            bot = bundle / "meshing-around-bot"
            bot.write_text("#!/bin/sh\nexit 0\n")
            bot.chmod(0o755)
            workspace = root / "runtime"
            result, executable = prepare_workspace(bundle, workspace)
            self.assertEqual(result, workspace)
            self.assertEqual(executable, bot)
            self.assertEqual((workspace / "config.ini").read_text(),
                             "[interface]\ntype = tcp\n")
            (workspace / "config.ini").write_text("custom settings")
            prepare_workspace(bundle, workspace)
            self.assertEqual((workspace / "config.ini").read_text(), "custom settings")

    def test_fails_if_bot_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "payload").mkdir()
            with self.assertRaises(FileNotFoundError):
                prepare_workspace(root, root / "runtime")


if __name__ == "__main__":
    unittest.main()
