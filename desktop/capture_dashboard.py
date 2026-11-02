"""Best-effort desktop GUI screenshot on a macOS CI runner.

This is a real dashboard render with no bot started or radio connections made.
No simulated connection status is displayed. Some hosted runners have no
usable WindowServer session; the screenshot step is optional.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tkinter as tk

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "desktop"))


def capture(destination: pathlib.Path) -> None:
    from dashboard import launch

    original = tk.Tk

    class TimedTk(original):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Meshing Around — UI preview (no bot running)")
            self.after(2000, self.destroy)
            self.after(700, lambda: subprocess.run(
                ["screencapture", "-x", str(destination)],
                check=False, timeout=5,
            ))

    tk.Tk = TimedTk
    try:
        launch(ROOT, ROOT / "mesh_bot.py", lambda address: False)
    finally:
        tk.Tk = original
    if not destination.is_file() or destination.stat().st_size < 1000:
        raise RuntimeError("No usable macOS desktop screenshot was captured")


if __name__ == "__main__":
    capture(pathlib.Path(sys.argv[1]).resolve())
