# Core Dispatch: Live Supabase Auth, Generation, And Evidence Wiring

Date: 2026-05-22

Status: ready for Core implementation.

## Why This Exists

The current iPhone build is old, and the current repo code still uses a local Alpha session flag for Apple ID access. A device test will not prove Supabase Auth until Core wires the Sign in with Apple identity token into Supabase and uses the resulting Supabase session/JWT for Edge Function calls.

## Current Repo Finding

- `MusicAtlasController/Views/RootView.swift` imports `AuthenticationServices` and presents `SignInWithAppleButton`.
- `recordAppleIdentityAuthorization` currently sets `waymark.alpha1.apple_identity_authorized` locally and shows "Apple ID sign-in completed for this Alpha session."
- The access screen still says full account persistence and Supabase identity are blocked.
- There is no checked-in `.entitlements` file or `CODE_SIGN_ENTITLEMENTS` setting for Sign in with Apple.
- `SupabaseMissionClientConfig`, `MissionGenerationClient`, and `EvidenceUploadClient` exist only as boundaries/stubs. There is no live `URLSession` client for Supabase Auth, `generate-first-mission-batch`, or `submit-alpha-evidence`.

Relevant files:

- `MusicAtlasController/Views/RootView.swift`
- `MusicAtlasController/Services/MissionLoader.swift`
- `MusicAtlasController/Services/SessionExporter.swift`
- `docs/infra/supabase_app_config_contract_v0_1.md`
- `docs/infra/supabase_alpha1_auth_generation_evidence_contract_v0_1.md`
- `docs/infra/supabase_live_deploy_report_2026_05_22.md`

## Backend State Core Can Rely On

Project:

- Supabase project URL: `https://ewuffhezhgyskcfyzkvw.supabase.co`
- Generate function: `generate-first-mission-batch`
- Evidence function: `submit-alpha-evidence`

Verified live:

- migrations applied
- Edge Function secrets set, including `OPENAI_API_KEY`
- `generate-first-mission-batch` live smoke passed with `status=app_import_candidate`
- `submit-alpha-evidence` live smoke passed and persisted an evidence row

Still not verified:

- Sign in with Apple -> Supabase Auth user/session on device
- app-authenticated evidence upload with `user_id_present=true`

## Required Core Work

1. Add Sign in with Apple capability to the app target.
   - Add an entitlements file if needed.
   - Ensure the Xcode target has `com.apple.developer.applesignin`.
   - Preserve the current bundle ID unless Product/Release changes it: `com.vytisstudios.MusicAtlasController`.

2. Replace local-only Apple identity completion with real Supabase Auth.
   - Generate and store a raw nonce for the Apple request.
   - Send the SHA-256 nonce to Apple in `ASAuthorizationAppleIDRequest`.
   - On completion, extract `ASAuthorizationAppleIDCredential.identityToken`.
   - Exchange the Apple ID token with Supabase Auth using provider `apple` and the raw nonce.
   - Persist the Supabase session as long as possible, using Keychain or the Supabase Swift client session store.
   - Gate first-run access on a valid Supabase session plus Apple Music authorization, not only a local boolean.

   Supabase Swift reference:
   - `supabase.auth.signInWithIdToken(credentials: OpenIDConnectCredentials(provider: .apple, idToken: ..., nonce: ...))`
   - https://supabase.com/docs/reference/swift/v1/auth-signinwithidtoken

3. Add app-safe Supabase config.
   - Do not hardcode service-role keys or OpenAI keys.
   - Use the Supabase project URL and anon/publishable key only.
   - Prefer an untracked local xcconfig or build setting for the anon/publishable key unless Release approves checking it in.

4. Implement a live mission generation client.
   - `POST /functions/v1/generate-first-mission-batch`
   - Headers:
     - `apikey: <anon/publishable key>`
     - `Authorization: Bearer <Supabase session access_token>`
     - `Content-Type: application/json`
   - Request should use the Survey Evidence Export / digest contract, not hidden simulator truth.
   - Import missions only when response `status == "app_import_candidate"` and `app_missions` is non-empty.
   - Preserve failure/support artifacts for `review_needed`, `blocked`, or `failed`.

5. Implement app-authenticated evidence upload, but keep automatic upload disabled until policy approval.
   - `POST /functions/v1/submit-alpha-evidence`
   - Same headers as generation.
   - Include consent fields only after terms/privacy acceptance.
   - For now, manual `Share Evidence Backup` remains the visible fallback.
   - Device smoke target: backend response has `user_id_present=true`.

6. Add tests or debug-only diagnostics that prove:
   - local first-run state does not mark account connected without Supabase session
   - Supabase Auth session survives relaunch when valid
   - generation imports only `app_import_candidate`
   - evidence upload sends the Supabase session JWT

## Device/TestFlight Handoff

After Core implements the above:

1. Build and install a new local device build or upload a new TestFlight build.
2. On iPhone, complete:
   - privacy gate
   - Sign in with Apple
   - Apple Music authorization
   - onboarding
   - Survey
3. Confirm generation creates/imports first missions.
4. Run one manual evidence upload/share backup path.
5. Infrastructure will verify rows:
   - `alpha_generation_runs`
   - `alpha_evidence_artifacts`
   - evidence upload response has `user_id_present=true`

## Do Not Do

- Do not store service-role keys in app code.
- Do not ship prebuilt missions as user content.
- Do not use anonymous Supabase JWT as the final Alpha identity path.
- Do not enable automatic evidence upload until privacy/retention/deletion/support policy is approved.
- Do not mark Apple ID connected from local state alone once live auth is enabled.
