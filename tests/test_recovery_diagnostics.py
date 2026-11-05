import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
from recovery_diagnostics import RecoveryDiagnostics, classify

class DiagnosticsTests(unittest.TestCase):
    def test_counts_and_last_event(self):
        d = RecoveryDiagnostics()
        self.assertEqual(d.record("radio disconnected"), "disconnected")
        self.assertEqual(d.record("retrying interface"), "retrying")
        self.assertEqual((d.disconnects, d.retries), (1, 1))
        self.assertIn("Disconnects: 1", d.summary())
    def test_unrelated_lines(self):
        self.assertIsNone(classify("message received"))

if __name__ == "__main__":
    unittest.main()
