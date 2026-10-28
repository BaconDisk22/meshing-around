"""Desktop entry point for Meshing Around."""
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parent.parent
BOT = ROOT / "mesh_bot.py"


def check_tcp(host: str, port: int = 4403) -> bool:
    """TCP reachability only; this is not a Meshtastic handshake."""
    host = host.strip()
    if ":" in host:
        name, sep, number = host.rpartition(":")
        if not name or not number.isdigit():
            raise ValueError("Expected hostname:port")
        host, port = name, int(number)
    if not host or not 1 <= port <= 65535:
        raise ValueError("Invalid host or port")
    with socket.create_connection((host, port), timeout=4):
        return True


def main() -> None:
    if not BOT.is_file():
        raise FileNotFoundError(BOT)
    if "--check" in sys.argv:
        print("DESKTOP_FOUNDATION_OK")
        return
    from dashboard import launch
    launch(ROOT, BOT, check_tcp)


if __name__ == "__main__":
    main()
