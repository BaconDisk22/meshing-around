# Phase 7: Intel Mac beta release gate

The existing Intel Mac workflow builds the app and DMG for pull requests and
main pushes. It does **not** publish a release on those events.

A maintainer can intentionally publish a beta by pushing a tag such as
`v0.1.0-beta.1`. The workflow then:

1. Builds the x86_64 app and DMG on an Intel macOS runner.
2. Runs unit tests, bundle validation and the packaged app self-test.
3. Validates the beta tag and creates SHA256SUMS.txt for the DMG.
4. Publishes a **GitHub prerelease**, not a stable release, only after success.

This does not notarize the app or prove real-radio connectivity. Before
publishing a beta tag, inspect the pull-request build, download the artifact,
and test the GUI and Wi-Fi/TCP radio on a real Intel Mac running Tahoe 26.7.1.

The beta release is never triggered by merging this PR alone.
