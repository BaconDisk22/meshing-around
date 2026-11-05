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

    def test_first_config_defaults_to_wifi_radio(self):
        from mac_app import mac_defaults
        template = ("[interface]\ntype = serial\nport = /dev/ttyACM0\n# hostname = meshtastic.local\n"
                    "[interface2]\nenabled = False\ntype = serial\nport = /dev/ttyACM0\n")
        result = mac_defaults(template)
        self.assertIn("[interface]\ntype = tcp\nhostname = meshtastic.local\n# hostname", result)
        self.assertIn("[interface2]\nenabled = False\ntype = serial\nport = /dev/ttyACM0\n", result)

    def test_shipped_template_gets_mac_defaults(self):
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
        from mac_app import mac_defaults
        from radio_config import read_radio
        template = pathlib.Path(__file__).resolve().parents[1] / "config.template"
        with tempfile.TemporaryDirectory() as directory:
            config = pathlib.Path(directory) / "config.ini"
            config.write_text(mac_defaults(template.read_text(encoding="utf-8")))
            self.assertEqual(read_radio(config), ("tcp", "meshtastic.local"))

    def test_fails_if_bot_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "payload").mkdir()
            with self.assertRaises(FileNotFoundError):
                prepare_workspace(root, root / "runtime")


if __name__ == "__main__":
    unittest.main()
