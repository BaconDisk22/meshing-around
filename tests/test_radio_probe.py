"""Radio probe tests requiring no radio hardware."""
import pathlib
import sys
import unittest
from unittest.mock import patch

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

    def test_tcp_retry_recovers_after_temporary_failure(self):
        expected = {"node_num": 1}
        with patch.object(radio_probe, "probe", side_effect=[ConnectionError("dropped"), expected]) as probe, \
             patch.object(radio_probe.time, "sleep") as sleep:
            self.assertEqual(radio_probe.probe_with_retry("tcp", "10.0.0.76:4403"), expected)
            self.assertEqual(probe.call_count, 2)
            sleep.assert_called_once_with(0.5)

    def test_tcp_retry_stops_after_bounded_attempts(self):
        with patch.object(radio_probe, "probe", side_effect=ConnectionError("offline")) as probe:
            with self.assertRaises(ConnectionError):
                radio_probe.probe_with_retry("tcp", "radio.local", attempts=2, delay=0)
            self.assertEqual(probe.call_count, 2)

    def test_non_tcp_transport_is_not_retried(self):
        with patch.object(radio_probe, "probe", side_effect=ConnectionError("offline")) as probe:
            with self.assertRaises(ConnectionError):
                radio_probe.probe_with_retry("serial", "/dev/cu.usbmodem1", delay=0)
            probe.assert_called_once()

    def test_describe(self):
        text = radio_probe.describe({"long_name": "Base", "short_name": "BS", "hardware": "RAK4631",
                                     "firmware": "2.7.15", "node_num": 1})
        self.assertEqual(text, "Connected to Base (BS) • RAK4631 • firmware 2.7.15")


if __name__ == "__main__":
    unittest.main()
