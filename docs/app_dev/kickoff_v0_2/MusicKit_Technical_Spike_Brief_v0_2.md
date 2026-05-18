# MusicKit Technical Spike Brief v0.2

## Objective

Prove that the app can use MusicKit on a physical iPhone to authorize Apple Music access, search the Apple Music catalog, resolve at least one sample mission item, play it, and export a reaction session.

## Required Apple setup

### 1. Apple Developer account and App ID

- Use an Apple Developer account capable of signing an iOS app on a physical device.
- Create/configure an App ID for the app bundle identifier.
- Enable the MusicKit service/capability for the App ID where required by Apple Developer portal setup.
- Use automatic signing only if it produces a provisioning profile with the required MusicKit capability.

Apple’s MusicKit docs describe Apple-platform integration through the Swift MusicKit framework and automatic token handling when MusicKit is enabled for the app/App ID.

### 2. Xcode target capabilities

- Add MusicKit / Apple Music capability in the app target if available in Xcode for the configured account/team.
- Confirm the app builds and signs for a physical iPhone.

### 3. Info.plist usage description

Add `NSAppleMusicUsageDescription` to Info.plist with a user-facing purpose string.

Recommended initial value:

```text
Music Atlas Controller uses Apple Music access to find and play tracks from your discovery missions and save listening feedback.
```

### 4. Music authorization states

The app must explicitly handle and display these authorization states:

- `notDetermined`
- `denied`
- `restricted`
- `authorized`

Behavior:

- If `notDetermined`, request authorization.
- If `denied` or `restricted`, block MusicKit search/playback and show recovery guidance.
- If `authorized`, allow resolution/playback steps.

### 5. Apple Music subscription / playback capability

Before playback, check that the current user/device can play Apple Music catalog content.

Implementation may use MusicKit subscription APIs and/or StoreKit cloud service capability APIs as appropriate. The UI must expose whether playback is allowed, unavailable, or unknown.

Acceptance requires actual playback on a physical iPhone. Merely resolving catalog metadata is not sufficient.

### 6. Catalog search/resolution

- Use MusicKit catalog search for mission item title/artist/album.
- Store the selected Apple Music catalog ID and returned metadata.
- Persist the storefront/region/country context if available.
- If results are ambiguous, mark item `ambiguous` and allow manual selection or skip.
- If no result, mark `unresolved` with reason.
- If unavailable in region/subscription, mark `unavailable_region` or `unavailable_subscription`.

### 7. Playback

- Use MusicKit playback APIs to queue and play the resolved catalog item.
- Acceptance requires playing at least one resolved track on a physical iPhone.
- Capture errors as exportable data, not just console logs.

### 8. Physical iPhone testing

Required test environment:

- Signed build installed on physical iPhone.
- Apple Music app installed and account signed in.
- Active Apple Music subscription or an account/device state that can play catalog tracks.
- Network connection.
- Region/storefront availability for at least one sample mission item.

Simulator-only testing is not accepted for the spike.

## Known risks

- Apple Music catalog availability varies by storefront/region.
- User authorization may be denied/restricted.
- Subscription state may block playback.
- A catalog search may return live, remastered, karaoke, tribute, or duplicate versions.
- Apple Music may require account/app state readiness on device.
- Playlist/library mutation is out of scope for this spike; avoid confusing it with playback.

## Spike implementation notes

Prefer transparent debug UI over hidden logs:

- authorization state
- subscription/playback capability
- storefront/region if known
- search query
- selected catalog ID
- resolution status
- playback status
- export validation status

## Source notes for MusicKit assumptions

This package is written for implementation planning, not as legal/App Review advice. It uses the following Apple developer references as the current technical baseline:

- MusicKit overview: https://developer.apple.com/musickit/
- MusicKit framework docs: https://developer.apple.com/documentation/MusicKit/
- MusicKit automatic token generation: https://developer.apple.com/documentation/musickit/using-automatic-token-generation-for-apple-music-api
- Apple Music API overview: https://developer.apple.com/documentation/applemusicapi/
- NSAppleMusicUsageDescription: https://developer.apple.com/documentation/bundleresources/information-property-list/nsapplemusicusagedescription
- Requesting access to Apple Music library: https://developer.apple.com/documentation/storekit/requesting-access-to-apple-music-library
- SKCloudServiceController / capabilities: https://developer.apple.com/documentation/storekit/skcloudservicecontroller
- MusicCatalogSearchRequest: https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest
- MusicCatalogResourceRequest: https://developer.apple.com/documentation/musickit/musiccatalogresourcerequest
- MusicPlayer: https://developer.apple.com/documentation/musickit/musicplayer
- Create a new library playlist: https://developer.apple.com/documentation/applemusicapi/create-a-new-library-playlist
