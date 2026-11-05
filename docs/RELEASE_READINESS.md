# Meshing Around — Release readiness checklist

This document is a checklist, not a release approval. Do not publish until the checks below are complete.

## Automated verification
- [ ] All unit tests pass on current main
- [ ] Intel Mac app and DMG GitHub Actions build succeeds on current main
- [ ] Downloaded application launches from Finder on an Intel Mac
- [ ] No regression in TCP hostname:port parsing and radio configuration backup
- [ ] No unexpected transmission during a radio connection probe

## Physical radio checks
- [ ] Test Wi-Fi/TCP connection against a real Meshtastic radio
- [ ] Verify bot start/stop with the radio connected
- [ ] Disconnect Wi-Fi or power down radio, verify disconnect handling and bounded retries
- [ ] Restore the radio and verify recovery
- [ ] Verify app quit while bot is running and during reconnect
- [ ] Repeat using the available Seeed T1000-E and RAK4631 where their interfaces permit

## Release decision
- [ ] Confirm no open blocker bugs or failing checks
- [ ] Review logs for private addresses, node information, or secrets before sharing
- [ ] Confirm version, changelog, and download artifacts
- [ ] Obtain explicit approval before publishing a release
