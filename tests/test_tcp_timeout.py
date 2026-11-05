import pathlib
import socket
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
from launcher import check_tcp

class TimeoutTests(unittest.TestCase):
    def test_timeout_reports_endpoint(self):
        with patch("launcher.socket.create_connection", side_effect=socket.timeout("timed out")):
            with self.assertRaisesRegex(TimeoutError, "radio.local:4403"):
                check_tcp("radio.local:4403")

if __name__ == "__main__":
    unittest.main()
