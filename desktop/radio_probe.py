"""Real Meshtastic handshake checks for the desktop app.

Unlike launcher.check_tcp, these open a Meshtastic protocol session and read
the radio's node info. Nothing is transmitted on the mesh.
"""
from __future__ import annotations

from radio_config import validate

TIMEOUT = 20


def split_host(endpoint: str) -> tuple[str, int]:
    host, sep, port = endpoint.rpartition(":")
    if sep and host and port.isdigit():
        return host, int(port)
    return endpoint, 4403


def open_interface(mode: str, endpoint: str):
    mode, endpoint = validate(mode, endpoint)
    if mode == "tcp":
        from meshtastic.tcp_interface import TCPInterface
        host, port = split_host(endpoint)
        return TCPInterface(hostname=host, portNumber=port, noNodes=True, timeout=TIMEOUT)
    if mode == "serial":
        from meshtastic.serial_interface import SerialInterface
        return SerialInterface(devPath=endpoint, noNodes=True, timeout=TIMEOUT)
    from meshtastic.ble_interface import BLEInterface
    return BLEInterface(endpoint, noNodes=True, timeout=TIMEOUT)


def probe(mode: str, endpoint: str) -> dict:
    """Connect, read the local node identity, then disconnect."""
    interface = open_interface(mode, endpoint)
    try:
        info = interface.getMyNodeInfo() or {}
        if not info:
            raise ConnectionError("Radio did not report node info")
        user = info.get("user", {})
        metadata = getattr(interface, "metadata", None)
        return {
            "long_name": user.get("longName", "?"),
            "short_name": user.get("shortName", "?"),
            "hardware": user.get("hwModel", "?"),
            "firmware": getattr(metadata, "firmware_version", "") or "?",
            "node_num": info.get("num"),
        }
    finally:
        interface.close()


def describe(result: dict) -> str:
    return (f"Connected to {result['long_name']} ({result['short_name']}) • "
            f"{result['hardware']} • firmware {result['firmware']}")


def serial_ports() -> list[str]:
    """USB serial devices that look like Meshtastic radios."""
    from meshtastic.util import findPorts
    return findPorts(eliminate_duplicates=True)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: radio_probe.py tcp|ble|serial ENDPOINT")
        return 2
    try:
        print("RADIO_PROBE_OK " + describe(probe(argv[0], argv[1])), flush=True)
        return 0
    except Exception as exc:  # report any failure as a clean, non-zero result
        print(f"RADIO_PROBE_FAILED {type(exc).__name__}: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
