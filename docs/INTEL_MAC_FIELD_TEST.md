# Intel Mac field-test checklist

Use this checklist before declaring the Meshing Around desktop beta hardware-verified. CI packaging and headless smoke checks are **not** substitutes for these tests.

## Setup

- [ ] Download the artifact from a successful Intel Mac GitHub Actions run.
- [ ] Install and open the application on a physical Intel x86_64 Mac.
- [ ] Record macOS version, application build, and radio firmware version.
- [ ] Confirm the app launches, navigates between all five pages, and exits without Force Quit.

## Radio and bot

- [ ] Select TCP and enter the actual Wi-Fi radio address and port.
- [ ] Save the settings; verify the unsaved-settings indicator resets.
- [ ] Test the connection with the bot stopped; confirm radio identification.
- [ ] Start the bot, observe normal status and output, then stop it cleanly.
- [ ] Disconnect Wi-Fi or power off the radio; observe errors and reconnect behavior.
- [ ] Restore the radio; confirm recovery and no duplicate bot processes.
- [ ] Verify no unwanted transmissions occurred during connection tests.

## Dashboard and screenshots

- [ ] Inspect text contrast and layout on Dashboard, Connection, Bot Controls, Logs, and Settings.
- [ ] Check narrow window sizes and both available theme options.
- [ ] Search logs, advance to another match, reset search, and export logs.
- [ ] Capture genuine screenshots after removing private messages, IP addresses, node identifiers, GPS coordinates, and credentials.
- [ ] Inspect the image before embedding it in the README.

## Result

Tester/date:
Mac/macOS:
Radio/firmware:
App build or workflow run:
Pass/fail notes:
Known issues:

**Release rule:** Do not mark live radio functionality verified or publish a stable release until the hardware steps have been completed and recorded.
