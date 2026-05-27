# Alpha Evidence Upload Recommendation v0.1

Generated: 2026-05-22

## Original Recommendation

For the first TestFlight build, keep evidence collection manual/export-first and do not add a second upload Edge Function unless the team decides manual export is too fragile.

Reason:

- Core already produces exportable evidence.
- Atlas ingestion remains provisional/reviewed.
- Trusted Alpha tester count is small.
- Privacy, retention, deletion, and support copy are still product decisions.
- Adding upload now risks turning Supabase into accidental sync/account infrastructure.

## Product Update 2026-05-22

Product now prefers automatic or scheduled Supabase evidence upload if engineering can support it safely with clear disclosures. Manual `Share Evidence` should remain as fallback/support.

Updated recommendation:

- Design the upload endpoint now.
- Do not silently upload evidence until privacy/terms, retention, deletion, and support access policy are approved.
- Upload after clear milestones or scheduled batches, not as full background sync.
- Use Sign in with Apple / Supabase identity if available; otherwise use trusted Alpha tester aliases only with explicit consent.
- Keep app evidence provisional and append-only; do not write promoted Atlas truth.
- Keep service-role keys out of the app.

## What To Build Now

Build and preserve:

- local app export/share path
- `alpha_evidence_artifacts` table from the migration
- app evidence envelope contract
- support runbook for collecting exports
- future endpoint placeholder in docs only

## Future Endpoint Shape

If manual export becomes the bottleneck, add:

```text
POST /functions/v1/upload-alpha-evidence-artifact
```

Request:

```json
{
  "client_artifact_id": "ios-generated-stable-id",
  "tester_alias": "trusted-alpha-001",
  "artifact_type": "reaction_session",
  "schema_version": "reaction_session.v0.2",
  "payload": {},
  "client_created_at": "2026-05-22T12:00:00Z"
}
```

Do not enable automatic upload until Product approves:

- tester consent language
- data retention policy
- deletion/reset behavior
- support access policy
- whether notes/user vocabulary are uploaded automatically
