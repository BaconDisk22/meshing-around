"""Best-effort real desktop screenshot capture on a logged-in macOS GUI session.

This script never synthesizes screenshots. It exits nonzero if no usable GUI
session or capture is available; the CI step is explicitly optional.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time


def capture(target: Path) -> int:
    if sys.platform != "darwin":
        print("Screenshots require macOS", file=sys.stderr)
        return 2
    if not os.environ.get("DISPLAY") and not os.environ.get("TERM_PROGRAM"):
        print("No confirmed GUI session; attempting macOS capture anyway")
    target.parent.mkdir(parents=True, exist_ok=True)
    launcher = Path(__file__).with_name("launcher.py")
    proc = subprocess.Popen([sys.executable, str(launcher)], cwd=launcher.parent.parent,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        time.sleep(6)
        if proc.poll() is not None:
            print("Desktop application exited before capture", file=sys.stderr)
            return 3
        result = subprocess.run(["screencapture", "-x", str(target)],
                                capture_output=True, text=True, timeout=20)
        if result.returncode or not target.is_file() or target.stat().st_size < 1000:
            target.unlink(missing_ok=True)
            print("No usable macOS screenshot: " + result.stderr.strip(), file=sys.stderr)
            return 4
        print(f"Captured real desktop screen: {target}")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: capture_dashboard.py OUTPUT.png")
    raise SystemExit(capture(Path(sys.argv[1])))
