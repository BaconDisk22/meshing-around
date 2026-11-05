"""Classify bot log lines without assuming that a radio is connected."""
from __future__ import annotations


def classify(line: str) -> str | None:
    value = line.lower()
    if "disconnect" in value or "connection lost" in value:
        return "disconnected"
    if "retry" in value or "reconnect" in value:
        return "retrying"
    if "connected" in value or "connection established" in value:
        return "reported_connected"
    return None


class RecoveryDiagnostics:
    def __init__(self):
        self.disconnects = 0
        self.retries = 0
        self.last_event = "No connection events recorded"

    def record(self, line: str) -> str | None:
        event = classify(line)
        if event == "disconnected":
            self.disconnects += 1
        elif event == "retrying":
            self.retries += 1
        if event:
            self.last_event = event
        return event

    def summary(self) -> str:
        return f"Disconnects: {self.disconnects} | retries: {self.retries} | last: {self.last_event}"
