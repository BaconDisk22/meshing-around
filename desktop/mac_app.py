"""Frozen macOS entry point.

Runtime configuration and bot working files live outside the signed app bundle.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

from dashboard import launch


def prepare_workspace() -> tuple[Path, Path]:
    if not getattr(sys, "frozen", False):
        raise RuntimeError("mac_app.py is intended for packaged execution")
    bundled = Path(sys._MEIPASS)
    source = bundled / "payload"
    bot_binary = bundled / "meshing-around-bot"
    if not source.is_dir() or not bot_binary.is_file():
        raise FileNotFoundError("Application resources or bundled bot executable missing")
    workspace = Path.home() / "Library" / "Application Support" / "MeshingAround" / "runtime"
    workspace.mkdir(parents=True, exist_ok=True)
    # Do not overwrite user configuration or runtime data on subsequent launches.
    for item in source.iterdir():
        destination = workspace / item.name
        if destination.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)
    return workspace, bot_binary


def main() -> None:
    workspace, bot = prepare_workspace()
    from launcher import check_tcp
    launch(workspace, bot, check_tcp)


if __name__ == "__main__":
    main()
