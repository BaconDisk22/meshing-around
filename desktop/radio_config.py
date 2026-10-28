"""Safe radio configuration editing, independent of Tk and radio hardware."""
from __future__ import annotations

import configparser
import os
from pathlib import Path
import shutil
import tempfile

TRANSPORTS = ("tcp", "ble", "serial")


def validate(mode: str, endpoint: str) -> tuple[str, str]:
    mode = mode.strip().lower()
    endpoint = endpoint.strip()
    if mode not in TRANSPORTS:
        raise ValueError("Transport must be TCP, BLE or serial")
    if not endpoint:
        raise ValueError("Enter a radio address or device path")
    if "\n" in endpoint or "\r" in endpoint:
        raise ValueError("Address must be a single line")
    if mode == "tcp":
        host, sep, port = endpoint.rpartition(":")
        if sep and port.isdigit() and host:
            if not 1 <= int(port) <= 65535:
                raise ValueError("TCP port must be 1-65535")
        elif ":" in endpoint:
            raise ValueError("Use hostname or hostname:port")
    return mode, endpoint


def read_radio(path: Path) -> tuple[str, str]:
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(path, encoding="utf-8")
    mode = cfg.get("interface", "type", fallback="tcp").lower()
    if mode not in TRANSPORTS:
        mode = "tcp"
    key = {"tcp": "hostname", "ble": "mac", "serial": "port"}[mode]
    return mode, cfg.get("interface", key, fallback="")


def save_radio(path: Path, template: Path, mode: str, endpoint: str) -> None:
    """Preserve unrelated settings and write atomically with a backup."""
    mode, endpoint = validate(mode, endpoint)
    path = Path(path)
    template = Path(template)
    source = path if path.exists() else template
    if not source.is_file():
        raise FileNotFoundError(f"No configuration template: {source}")
    cfg = configparser.ConfigParser(interpolation=None)
    with source.open(encoding="utf-8") as handle:
        cfg.read_file(handle)
    if not cfg.has_section("interface"):
        cfg.add_section("interface")
    cfg.set("interface", "type", mode)
    cfg.set("interface", {"tcp": "hostname", "ble": "mac", "serial": "port"}[mode], endpoint)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=".radio-", suffix=".tmp", delete=False) as handle:
            temp_name = handle.name
            cfg.write(handle)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
