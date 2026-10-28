# Desktop foundation (Phase 1)

This folder contains the initial desktop launcher for the BaconDisk22 fork.
It leaves the existing Meshtastic bot and configuration unchanged.

Run from the repository root with the bot's Python dependencies installed:

    python desktop/launcher.py

**Test connection** opens a real Meshtastic session over TCP, BLE or USB,
reads the radio's name, hardware and firmware, then disconnects. Nothing is
sent on the mesh. Stop the bot first; a radio accepts one client at a time.
**Find USB radios** fills in the first detected USB serial device.

New installs default to Wi-Fi/TCP at `meshtastic.local`. **Start bot** runs the existing mesh_bot.py with
its existing configuration and displays its output.

CI runs on an Intel macOS runner and checks Python syntax and the headless
entry point. This is **not yet** a packaged .app or .dmg.

Next: configuration editor, transport support (Wi-Fi/TCP, BLE, USB), modern
five-page dashboard, persistent themes, packaging and release automation.
