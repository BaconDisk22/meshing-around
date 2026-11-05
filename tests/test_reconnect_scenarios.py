"""Hardware-free simulation of a TCP radio dropping and recovering."""
import pathlib
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
import radio_probe

class ReconnectScenarios(unittest.TestCase):
    def test_radio_offline_then_back_online(self):
        expected = {"node_num": 123}
        with patch.object(radio_probe, "probe", side_effect=[ConnectionError("offline"), expected]) as p, patch.object(radio_probe.time, "sleep"):
            self.assertEqual(radio_probe.probe_with_retry("tcp", "10.0.0.76:4403"), expected)
            self.assertEqual(p.call_count, 2)

    def test_offline_radio_stops_after_budget(self):
        with patch.object(radio_probe, "probe", side_effect=ConnectionError("offline")) as p, patch.object(radio_probe.time, "sleep"):
            with self.assertRaises(ConnectionError):
                radio_probe.probe_with_retry("tcp", "10.0.0.76:4403", attempts=3)
            self.assertEqual(p.call_count, 3)

if __name__ == "__main__":
    unittest.main()
