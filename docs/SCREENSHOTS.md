# Real desktop screenshots

The project only publishes screenshots captured from the actual Meshing Around application. A mockup or generated illustration must not be presented as an app screenshot.

## GitHub Actions capture

The [Intel Mac beta workflow](https://github.com/BaconDisk22/meshing-around/actions/workflows/intel-mac-app.yml) includes a best-effort `Capture dashboard screenshot` step. When it succeeds, download the `dashboard-screenshot` artifact from the workflow run. The screenshot may include the runner desktop; **inspect and crop it before publishing**. Headless runners can fail to capture an image; this does not fail the app build.

## Capture on a real Intel Mac

1. Install and launch the latest beta app.
2. Open **Dashboard**, with no personal messages, node identifiers, addresses, or credentials visible.
3. Use macOS **Shift-Command-4**, then press **Space**, and click the app window to capture it.
4. Repeat for **Connection**, **Bot Controls**, **Logs**, and **Settings**. Redact any identifying details before committing screenshots.
5. Add verified images to `docs/screenshots/` and embed them in the main README using relative links.

Suggested file names: `dashboard.png`, `connection.png`, `bot-controls.png`, `logs.png`, `settings.png`.

Do not claim the screenshots are verified until someone inspects the actual files. Screenshot capture is not a substitute for radio hardware testing.
