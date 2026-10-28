# Intel Mac desktop beta packaging

GitHub Actions workflow: **Intel Mac app and DMG (beta)**.

This first packaging stage builds on an Intel macOS runner using Python 3.12
and PyInstaller. It attempts to package the existing Meshtastic bot as a
separate executable and embeds it alongside the Tk desktop app. It produces
a click-to-open .app and a drag-to-Applications .dmg as workflow artifacts.

The app uses ~/Library/Application Support/MeshingAround/runtime for writable
bot files and config.ini. On first launch, tracked repository resources are
copied there. Existing files are not overwritten on later launches, so user
configuration is retained. This also means updated resource files are not
automatically migrated; that will need a future versioned migration system.

**Limitations:** Build and launch on macOS Tahoe 26.7.1 have not yet been
verified. The app is unsigned and unnotarized; macOS Gatekeeper may require
explicit approval. Some optional bot modules or hardware features may need
additional PyInstaller hooks. CI architecture validation alone does not
prove the GUI opens or the radio connects. Do not publish a stable release
until tested on a real Intel Mac.

After PR checks pass, run the workflow manually using Actions > Intel Mac app
and DMG (beta) > Run workflow, then download the artifact from the run.
