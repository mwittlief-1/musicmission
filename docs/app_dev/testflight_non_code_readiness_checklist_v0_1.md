# TestFlight Non-Code Readiness Checklist v0.1

Purpose: track everything outside the repo that must be ready before Waymark Alpha can be distributed through TestFlight.

Last checked against Apple documentation: 2026-05-22.

## Current Assumptions

- Apple Developer Program membership exists.
- App Store Connect contracts have been accepted.
- A physical-device build is already installed on the founder's iPhone.
- First Alpha is trusted/internal-first, then external trusted testers after physical QA and TestFlight Beta App Review.
- The TestFlight app must not ship with prebuilt missions as user content.
- First Alpha includes required privacy/terms, Apple ID + Apple Music connection, onboarding, Survey intake, and generated first mission batch.
- Product prefers Supabase evidence upload/sync if privacy/retention and engineering are ready; manual Share Evidence remains fallback.

## Apple Account And App Store Connect

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Confirm App Store Connect app record exists for the TestFlight target | Founder/Release | open | Xcode project bundle ID is currently `com.vytisstudios.MusicAtlasController`. App Store Connect bundle ID must match before upload. |
| Confirm app name/display name | Founder/Design | decided | App name is `Waymark`; update display name/TestFlight metadata before external testers. |
| Confirm SKU and primary language | Founder/Release | open | SKU is internal only but cannot be changed after app creation. |
| Confirm app category | Founder/Release | open | Needed for App Store metadata; invite can optionally hide approved app info. |
| Set age rating | Founder/Release | open | App-level App Store Connect property. Likely low-risk, but answer music/content questions accurately. |
| Confirm content rights | Founder/Release | open | App accesses Apple Music catalog content; confirm rights position is "permitted access through Apple Music/MusicKit, no bundled third-party media." |
| Confirm App ID capabilities | Founder/Core | open | MusicKit/Apple Music capability and signing team must match the Release archive. |
| Confirm latest agreements are still clear | Founder | done? | User reports contract acceptance. Re-check only if App Store Connect blocks upload or metadata editing. |

## TestFlight Setup

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Create an internal testing group | Founder/Release | open | Required before external testing. Use a small "Alpha Internal" group. |
| Add internal testers | Founder/Release | open | Apple currently supports up to 100 internal testers who are App Store Connect users with access to the app. |
| Decide external tester strategy | Founder/Product | open | Trusted named email invites are safer than a public link for Alpha 1. |
| Create external tester group | Founder/Release | blocked | Do this after physical-device QA passes. External testers can be up to 10,000, but Alpha should stay small. |
| Prepare "What to Test" text | Product/Release | open | See draft below. This appears when adding a build to a tester group. |
| Prepare Beta App Description | Product/Release | open | Required for external TestFlight test information. |
| Set Feedback Email | Founder/Release | open | Required for TestFlight test information; also reply-to address for tester invitations. |
| Fill TestFlight contact information | Founder/Release | open | Required for Beta App Review metadata. |
| Fill review notes | Product/Release | open | Must tell Apple how to test without a preloaded mission and how Apple Music requirements work. |
| Decide whether demo credentials are needed | Product/Release | open | Current app has no login; if Supabase auth changes that, provide non-expiring review credentials. |
| Submit first external build for Beta App Review | Founder/Release | blocked | Only after Release build, metadata, privacy, and QA are ready. Apple says the first external build requires review; later builds for the same version may not. |

## Privacy, Trust, And Support

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Publish privacy policy URL | Founder/Release | open | Apple requires a privacy policy URL for iOS app platforms. |
| Complete App Privacy answers | Founder/Release | open | Must reflect Sign in with Apple, Apple Music access, Survey evidence, mission evidence, generation logs, and any upload/sync behavior. |
| Write Alpha tester consent note | Product/Release | required | Explain Apple Music access, Survey evidence, mission evidence, generated missions, upload/share behavior, reset, retention, and deletion limits in plain language. |
| Define retention/deletion policy | Founder/Product | required | Needed before evidence is uploaded to Supabase or shared back to the team. |
| Define support channel | Founder/Release | open | Feedback email plus preferred Slack/Text/Email path for trusted Alpha testers. |
| Define incident pause procedure | Founder/Infra | open | If mission generation, privacy, or playback behavior is wrong: pause TestFlight group, expire build, rotate secrets if needed. |
| Decide evidence upload posture | Product/Infra | decided direction | Product prefers Supabase upload/sync if safe; manual Share Evidence fallback remains. |

## Export Compliance And Legal Metadata

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Answer export compliance questions | Founder/Release | open | Apple requires an export compliance determination for apps using encryption. If only Apple OS/network encryption is used, documentation may not be required, but the App Store Connect questions still need to be answered unless an Info.plist exemption is added. |
| Decide whether to add `ITSAppUsesNonExemptEncryption` | Core/Release | open | Only add after confirming the correct answer. This can reduce repeated encryption prompts. |
| Confirm no paid content/subscriptions in Alpha | Founder/Product | assumed | If monetization appears later, legal/account setup expands. |
| Confirm third-party content statement | Founder/Release | open | Make clear that Apple Music playback is through the user's Apple Music account and MusicKit; no music files are bundled. |

## Brand And Assets

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Final Alpha app name | Founder/Design | decided | Use `Waymark`. |
| App icon | Design/Core | open | Repo currently has no `.xcassets` app icon catalog discovered. Needed for a polished TestFlight install and App Store Connect metadata. |
| Launch screen posture | Design/Core | open | Info.plist currently has an empty `UILaunchScreen`; acceptable for spike, not polished. |
| Brand color/type/token pass | Design/Core | open | Alpha visual system is dark mode only. Token pass means reusable colors, type scale, spacing, radii, and semantic state colors. |
| Tester-facing copy pass | Product/Design | open | Empty states, import labels, export labels, and privacy language need a non-engineer pass. |
| Screenshots for design review | Design/Core | open | Not strictly required for internal TestFlight, useful for external invite/app info and brand review. |

## Tester Operations

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Tester roster | Founder | open | Name, email, iPhone model, iOS version, Apple Music subscription status. |
| Tester prerequisites | Founder/Release | open | TestFlight app installed, Apple Account usable for TestFlight, Apple Music access/subscription, enough time for a mission. |
| Tester welcome note | Product/Release | open | Include install steps, what to test, how to report feedback, how to reset local state. |
| Mission assignment plan | Product/Infra | blocked by live Supabase | No bundled missions. First mission batch should be generated after Survey completion. |
| Evidence return path | Product/Infra | open | Product prefers Supabase upload/sync after consent; keep Share Evidence fallback. |
| Feedback triage rhythm | Founder/Product | open | Decide daily review time, severity tags, and who files repo issues. |

## Build Upload And Release-Day Flow

| Step | Owner | Status | Notes |
| --- | --- | --- | --- |
| Increment version/build | Core/Release | open | Current Info.plist is version `0.2`, build `1`. Build number must uniquely increase for each upload. |
| Archive Release build in Xcode | Core/Release | open | Use approved signing team and bundle ID. |
| Upload through Xcode or Transporter | Founder/Core | open | Apple says a processed build must appear in App Store Connect before TestFlight distribution. |
| Wait for build processing email/status | Founder/Release | open | First upload creates/updates beta build record; build processing can take time. |
| Resolve missing compliance warnings | Founder/Release | open | Often export compliance. |
| Add build to internal group | Founder/Release | open | Start internal test before external submission. |
| Run physical QA checklist | Core/Founder | open | See `docs/app_dev/physical_device_musickit_qa_checklist.md`. |
| Add build to external group and submit review | Founder/Release | blocked | Requires metadata and test info. |

## Draft TestFlight Copy

### Beta App Description

Waymark is a private Alpha for testing an Apple Music-powered discovery loop. Testers accept Alpha privacy terms, connect with Apple ID and Apple Music, complete a guided onboarding and Survey intake, then receive a generated first mission batch. The app captures lightweight listening evidence for product calibration. This build does not include prebuilt user missions.

### What To Test

1. Install the build, accept Alpha terms, and connect Apple ID/Apple Music.
2. Complete the required onboarding and Survey intake.
3. Confirm the app generates or assigns a first mission batch after Survey completion.
4. Start a mission, play several tracks, and capture reactions and optional notes.
5. Review mission evidence and confirm Share Evidence or sync status behaves as expected.
6. Share any playback failures, confusing copy, missing state, crashes, privacy concerns, or moments where the app implies it knows more than it should.

### App Review Notes Draft

This beta requires Apple Music access for catalog search/playback and uses Apple ID sign-in for Alpha account continuity if enabled in the submitted build. The app does not include bundled music files and does not ship prebuilt user missions. On first launch, testers accept Alpha terms, connect Apple Music, complete onboarding and Survey intake, then receive a generated first mission batch. Evidence is Alpha/provisional and is used for product calibration.

## Sources

- Apple TestFlight overview: `https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/`
- Apple provide test information: `https://developer.apple.com/help/app-store-connect/test-a-beta-version/provide-test-information`
- Apple invite external testers: `https://developer.apple.com/help/app-store-connect/test-a-beta-version/invite-external-testers/`
- Apple add internal testers: `https://developer.apple.com/help/app-store-connect/test-a-beta-version/add-internal-testers/`
- Apple upload builds: `https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds`
- Apple app privacy: `https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/`
- Apple app information reference: `https://developer.apple.com/help/app-store-connect/reference/app-information/app-information/`
- Apple export compliance overview: `https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance/`
