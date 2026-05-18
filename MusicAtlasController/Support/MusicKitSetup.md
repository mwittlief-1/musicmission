# MusicKit Setup

Before physical-device acceptance testing:

1. Select a real Apple Developer team in Xcode.
2. Use a bundle identifier registered in Certificates, Identifiers & Profiles.
3. Enable the MusicKit app service for that App ID.
4. Rebuild and reinstall after the developer portal change has propagated.
5. Build and run on a physical iPhone signed into an Apple ID with Apple Music playback capability.
6. If iOS blocks first launch, trust the developer profile on the iPhone in Settings.

The app already includes `NSAppleMusicUsageDescription` in `Info.plist`. The MusicKit service still needs to be enabled for the App ID in the Apple Developer portal.

If live resolution reports `MusicKit.MusicTokenRequestError#5`, treat it as `developerTokenRequestFailed`. The first fix is to confirm MusicKit is enabled under the explicit App ID for `com.vytisstudios.MusicAtlasController`, then rebuild and reinstall the app.

## POC run path

Use **Development Stub** mode in the simulator:

1. Open Resolve.
2. Keep Service Mode set to Development Stub.
3. Resolve the mission or one item.
4. Open Player.
5. Simulate playback.
6. Save a reaction with a non-empty note.
7. Open Export.
8. Generate a Dev Stub Export Preview.

Use **Live MusicKit** mode only when a physical iPhone is paired:

1. Build and run on the paired iPhone.
2. If prompted that the developer is not trusted, open iPhone Settings, trust the developer profile, then launch again.
3. Request Apple Music authorization.
4. Open Resolve and switch Service Mode to Live MusicKit.
5. Resolve the mission or one item with MusicKit.
6. Open Player and play the resolved item with MusicKit.
7. Save a reaction with a non-empty note.
8. Open Export and confirm the mission readiness counts include resolved, played, and reacted evidence.
9. Generate an Acceptance Export Preview.

Acceptance export intentionally rejects simulator context and stub catalog IDs.
