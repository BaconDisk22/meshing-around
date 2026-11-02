# Automated desktop screenshot (experimental)

The Intel Mac CI workflow now attempts to render the **real desktop
Dashboard** in a macOS graphical session and capture a screenshot. The bot
is not started, no Meshtastic connection is attempted, and no radio status is
fabricated.

When capture works, download the `dashboard-screenshot` artifact from the
workflow run. The screenshot is not automatically committed to README:
GitHub-hosted macOS runners may not have a usable GUI session, and an
unverified screenshot must not replace a real desktop test.

The screenshot job is best effort and does not block the DMG build.
A real Intel Mac Tahoe 26.7.1 GUI and TCP radio test is still required
before claiming the app is working.
