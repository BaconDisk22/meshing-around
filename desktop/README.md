# Meshing Around — Intel Mac Desktop Beta

This folder contains the Tkinter desktop application and Intel macOS packaging helpers for the BaconDisk22 fork. The existing Meshtastic bot remains the backend.

## Launch from source

From the repository root with dependencies installed:

```bash
python desktop/launcher.py
```

## Desktop pages

- **Dashboard:** Bot process status, radio connection status, recent activity, and navigation shortcuts.
- **Connection:** Choose TCP, BLE, or serial; save settings, test the radio, or find a USB device. A connection test reads radio information and disconnects without transmitting a mesh message.
- **Bot Controls:** Start and stop the bot process. Stop it before editing or testing radio settings.
- **Logs:** Read bot output, export diagnostics, or clear the visible log.
- **Settings:** Change the persistent desktop theme.

The default Wi-Fi/TCP address is `meshtastic.local`. You can specify a reachable radio host and port (for example `192.168.1.50:4403`). The app also supports BLE and USB/serial selection, subject to hardware and platform compatibility.

## Intel Mac build

The [Intel Mac workflow](../.github/workflows/intel-mac-app.yml) builds an x86_64 `.app` and `.dmg` on a macOS Intel runner, runs automated checks, and uploads the `meshing-around-intel-mac-beta` artifact. The beta is not notarized. See [MAC_PACKAGING.md](MAC_PACKAGING.md) and [BETA_RELEASE.md](BETA_RELEASE.md).

## Screenshots

The build workflow has an optional `dashboard-screenshot` artifact step. Screenshot capture is best effort and should not be treated as a verified image until the capture is inspected. The main [README](../README.md) will display actual desktop screenshots once available.

## Validation status

CI exercises syntax, packaging, and headless smoke checks. A live radio connection, Bluetooth permissions, and UI appearance must still be checked on a physical Intel Mac before a stable release.
