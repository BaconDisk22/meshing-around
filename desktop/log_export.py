"""Export recent desktop diagnostics without overwriting existing files."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path


def export_logs(folder: Path, content: str, now=None) -> Path:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    for index in range(1000):
        suffix = f"-{index}" if index else ""
        target = folder / f"meshing-around-{stamp}{suffix}.log"
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(content)
            return target
        except FileExistsError:
            continue
    raise FileExistsError("Too many diagnostic exports for this timestamp")
