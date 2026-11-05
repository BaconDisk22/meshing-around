"""Radio probe tests requiring no radio hardware."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
import radio_probe


class RadioProbeTests(unittest.TestCase):
    def test_split_host(self):
        self.assertEqual(radio_probe.split_host("meshtastic.local"), ("meshtastic.local", 4403))
        self.assertEqual(radio_probe.split_host("10.0.0.5:4404"), ("10.0.0.5", 4404))

    def test_invalid_endpoint_rejected_before_connecting(self):
        with self.assertRaises(ValueError):
            radio_probe.probe("tcp", "")

    def test_unreachable_radio_reports_clean_failure(self):
        self.assertEqual(radio_probe.main(["tcp", "127.0.0.1:9"]), 1)

    def test_describe(self):
        text = radio_probe.describe({"long_name": "Base", "short_name": "BS", "hardware": "RAK4631",
                                     "firmware": "2.7.15", "node_num": 1})
        self.assertEqual(text, "Connected to Base (BS) • RAK4631 • firmware 2.7.15")


if __name__ == "__main__":
    unittest.main()
