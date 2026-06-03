# Album Track Sidecar Apple ID Backfill v1

Generated: 2026-05-29T03:29:30.237Z

Status: `complete`

## Policy

- Raw Apple payloads persisted: `false`
- No Apple catalog requests were made.
- Source data is accepted Apple link JSONL output only.
- Durable updates are Apple collection IDs, Apple track IDs, and derived Apple Music track URLs for existing sidecar rows.

## Counts

| Metric | Count |
| --- | ---: |
| Album sidecar album links considered | 2112 |
| Album sidecar album links used | 2112 |
| Album Apple collection IDs added to sidecar | 0 |
| Album Apple collection IDs already present | 2112 |
| Album ID conflicts | 0 |
| Album rows with Apple collection ID after backfill | 2112 |
| Album sidecar track links considered | 25030 |
| Album sidecar track links used | 25030 |
| Track Apple IDs added to sidecar | 738 |
| Track Apple IDs already present | 24292 |
| Track URLs derived and added | 738 |
| Track ID conflicts | 0 |
| Track rows with Apple track ID after backfill | 25030 |
| Total track rows | 28306 |
