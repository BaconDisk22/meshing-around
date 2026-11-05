"""Hardware-free regression tests for the existing bot's reconnect retry budget."""
import ast
import asyncio
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, Mock

SOURCE = Path(__file__).resolve().parents[1] / "modules" / "system.py"


def load_retry():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    function = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)
                    and node.name == "retry_interface")
    namespace = {"logger": Mock(), "asyncio": Mock(sleep=AsyncMock()),
                 "dont_retry_disconnect": False, "interface_retry_count": 3,
                 "exit_handler": Mock(side_effect=RuntimeError("retry exhausted"))}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace


class ReconnectRetryTests(unittest.TestCase):
    def test_missing_interface_consumes_retry_budget(self):
        ns = load_retry()
        ns.update(interface1=None, retry_int1=True, max_retry_count1=2,
                  interface1_type="tcp", hostname1="127.0.0.1:4403")
        ns["meshtastic"] = Mock()
        ns["meshtastic"].tcp_interface.TCPInterface.side_effect = OSError("offline")
        asyncio.run(ns["retry_interface"](1))
        self.assertEqual(ns["max_retry_count1"], 1)
        self.assertTrue(ns["retry_int1"])
        with self.assertRaisesRegex(RuntimeError, "retry exhausted"):
            asyncio.run(ns["retry_interface"](1))
        self.assertEqual(ns["max_retry_count1"], 0)

    def test_successful_reconnect_restores_budget(self):
        ns = load_retry()
        ns.update(interface1=None, retry_int1=True, max_retry_count1=2,
                  interface1_type="tcp", hostname1="127.0.0.1:4403")
        connected = object()
        ns["meshtastic"] = Mock()
        ns["meshtastic"].tcp_interface.TCPInterface.return_value = connected
        asyncio.run(ns["retry_interface"](1))
        self.assertIs(ns["interface1"], connected)
        self.assertFalse(ns["retry_int1"])
        self.assertEqual(ns["max_retry_count1"], 3)


if __name__ == "__main__":
    unittest.main()
