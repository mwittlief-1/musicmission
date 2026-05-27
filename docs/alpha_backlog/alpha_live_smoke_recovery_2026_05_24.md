# Alpha Live Smoke Recovery Packet

Date: 2026-05-24

Purpose: convert the latest physical-device/TestFlight findings into autonomous lane work. This packet supersedes the older assumption that generation/import was mostly solved. The live backend path is active, but Alpha now needs a more tolerant import posture and a client-to-backend diagnostic chain.

## PM Diagnosis

The live runs prove that the core path is real:

- Supabase Auth/generation access works well enough for the app to reach `generate-first-mission-batch`.
- Required Survey completion is reaching the backend with `10` displayed pages and `64-66` responses.
- The backend is generating structurally valid missions from Survey/Atlas/candidate context.
- At least one run returned `app_import_candidate` and imported one mission.

The live runs also expose the next blocker:

- `review_needed` is too strict for trusted Alpha. It blocks structurally valid generated routes that should either be imported with review flags or retried without freezing the tester.
- The app does not yet emit enough client audit artifacts to reconstruct Apple Music signal, Survey page construction, response export, generation request/result, and app import result.
- A small number of Survey responses can be quarantined because response state and displayed-page records are not yet fully explainable from Supabase.
- Backend audit rows are useful, but they start too late in the chain. The missing path is Apple Music -> Survey page selection -> Survey Evidence Export -> mission request -> generation result -> import result.

## Next Alpha Acceptance Target

The next build should let a trusted Alpha tester complete this path:

```text
Apple Music signal captured
-> required 10-page Survey generated from approved surfaces
-> Survey Evidence Export / digest packet created
-> up to 10 mission-generation attempts
-> 10 imported app-validated missions when possible
-> no hard block on isolated review_needed attempts
-> PM-readable audit artifacts available in Supabase
```

Minimum pass criteria:

- Survey records exactly `4` artist pages, `2` album pages, and `4` song pages.
- Every Survey response is explainable against a displayed page, or quarantine includes a concrete reason.
- Mission generation keeps attempting until it imports `10` missions or hits a real hard failure / max-attempt ceiling.
- `review_needed` rows are stored and visible, but do not end the whole Alpha run by themselves.
- The app logs client-side generation/import outcomes, including blocked status, validation errors, imported mission IDs, and run IDs.
- Manual support upload can submit diagnostic artifacts after consent; automatic upload remains off until privacy/retention/deletion copy is approved.

## Dispatch To All Lanes

```text
Please read docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md first, then open your lane file in docs/alpha_backlog. New work is under "Live Alpha Smoke Recovery Tasks". Complete all non-dependent tasks you can. If you hit a dependency, add it to your lane's Raised Issues table with the owning lane and exact needed artifact.
```

## P0 Cross-Lane Work

| task | owner | consumers | acceptance |
| --- | --- | --- | --- |
| Add trusted Alpha import tolerance for structurally valid `review_needed` generations. | Supabase / Mission Generation / Core | Core, Release QA | A single review-gated mission does not block the whole 10-mission batch; imported missions remain app-validated and review flags remain auditable. |
| Add client diagnostic artifacts. | Core / Supabase / Atlas | PM, Core, Survey, Mission Generation | Supabase can show Apple signal, page-selection audit, Survey export, request packet, generation result, and import result linked by session/request/run IDs. |
| Add Survey page-selection audit. | Survey / Core / Canonical Graph | PM, Atlas, Mission Generation | Each displayed tile has source, typed ref, Apple exposure flag, page intent, candidate basis, and prior-response context without hidden simulator truth. |
| Explain quarantined Survey responses. | Survey / Core / Atlas | PM, Release QA | Any quarantined response reports missing displayed page, missing ref, invalid state, duplicate, or schema mismatch. |
| Add live-run query/runbook. | Supabase / Infrastructure | PM, Release QA | One query or script summarizes one tester run end to end from auth/session through generation/import/evidence upload. |

## Lane Task Index

| lane | new task IDs | summary |
| --- | --- | --- |
| Core Waymark Build | `CWB-030` - `CWB-033` | Generation resilience, client audit capture/upload, Survey runtime audit wiring, device-smoke report. |
| Supabase / Infrastructure | `INF-020` - `INF-023` | Diagnostic schema/function support, alpha import tolerance, live audit view/script, runbook. |
| Mission Generation / Closed Loop | `MGN-015` - `MGN-017` | Review-needed relaxation policy, prompt/evaluator repair, 10-mission diversity/attempt semantics. |
| Survey Simulator | `SIM-017` - `SIM-019` | Page-selection audit contract, quarantine explanation, Apple/prior-response adaptive QA. |
| Canonical Music Graph | `CMG-021` - `CMG-022` | Candidate safety metadata and route-ready candidate pool review for fewer false review gates. |
| Atlas Schema | `ATL-018` - `ATL-019` | Diagnostic artifact classification and client audit link semantics without promoting Atlas truth. |

## Guardrails

- Do not ship prebuilt missions as user content.
- Do not import backend `blocked` output.
- Do not import malformed app missions just because the tester is trusted.
- Do not expose raw Apple Music payload, Survey ranking internals, run IDs, schemas, resolver details, or import errors in the normal tester UI.
- Do not turn diagnostic artifacts into promoted Atlas truth.
- Do not enable automatic uploads until privacy/retention/deletion/support language is approved.

## Open Product/Policy Dependencies

| dependency | owner | impact |
| --- | --- | --- |
| Final privacy/terms/retention/deletion/support copy | Product / Release | Blocks automatic diagnostic/evidence upload. Manual support upload can remain consent-gated. |
| Final app icon/art | Brand / Release | Blocks broader polish, not this recovery pass. |
| Whether alpha imports `review_needed` with flags or retries until `app_import_candidate` only | Product / Mission Generation / Infra | This packet recommends trusted Alpha import tolerance only when app mission validation passes and review flags are stored. |
| Long-term Survey generator location | Product / Survey / Core | Alpha can keep app-side dynamic provider; future architecture may move generation to a service. |
