"""Radio settings tests requiring no radio or Tk display."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
from radio_config import read_radio, save_radio, validate


class RadioConfigTests(unittest.TestCase):
    def test_reject_invalid(self):
        for mode, endpoint in (("mqtt", "radio"), ("tcp", ""), ("tcp", "radio:70000"),
                               ("ble", "device\nother")):
            with self.subTest(mode=mode, endpoint=endpoint):
                with self.assertRaises(ValueError):
                    validate(mode, endpoint)

    def test_save_preserves_unrelated_settings_and_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            template = root / "config.template"
            path = root / "config.ini"
            template.write_text("[interface]\ntype = serial\nport = /dev/ttyUSB0\n[general]\nwhoami = True\n")
            save_radio(path, template, "tcp", "radio.local:4403")
            self.assertEqual(read_radio(path), ("tcp", "radio.local:4403"))
            self.assertIn("whoami = True", path.read_text())
            save_radio(path, template, "serial", "/dev/cu.usbmodem101")
            self.assertEqual(read_radio(path), ("serial", "/dev/cu.usbmodem101"))
            self.assertTrue((root / "config.ini.bak").exists())


if __name__ == "__main__":
    unittest.main()
