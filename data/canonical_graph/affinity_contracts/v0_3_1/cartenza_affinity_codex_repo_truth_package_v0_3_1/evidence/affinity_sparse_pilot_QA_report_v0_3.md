# Affinity Retag Pilot v0.3 — QA Report

## PM decision status

This package is a sparse production simulation. It does **not** authorize graph-wide tagging or runtime ingestion.

## Counts

- Songs tagged: **120**
- Families covered: **18 / 18**
- Sample bucket distribution: **{'high': 40, 'medium': 40, 'deep': 40}**
- Average tags per song: **6.10**
- Median tags per song: **6.0**
- Min / max tags per song: **6 / 7**
- Tag count distribution: **{6: 108, 7: 12}**

## Ontology validation

- Canonical tags in ontology: **86**
- Unique canonical tags used: **78 / 86**
- Non-canonical tags: **0**
- Alias leakage: **0**

## Sparse-rule checks

- Songs under 5 tags: **0**
- Songs over 8 tags: **0**
- Empty `social_context` songs: **86 / 120 (71.7%)**
- `safe_gateway` count: **24**
- `context_dependent` count: **12**

## Review fields

- identity_review_needed: **0**
- tag_review_needed: **7**
- selection_bucket_review_needed: **0**
- review reason codes: **{'routing_caution_unclear': 5, 'tag_definition_ambiguous': 7}**

## Acceptance gate

| Gate | Result |
|---|---:|
| Average tags per song 6–8 | PASS |
| No alias leakage | PASS |
| No non-canonical tags | PASS |
| No family-wide blanket behavior | PASS — no tag appears as a full-family blanket in the sample |
| `safe_gateway` under control | PASS |
| `context_dependent` under control | PASS |
| At least 10–15% empty social_context | PASS |
| Bridge clusters still emerge naturally | PASS |
| False-nearby candidates receive caution metadata | PASS |

## QA conclusion

PASS: Sparse production simulation meets the PM acceptance gate and is a candidate basis for authorizing graph-wide song tagging after final PM review.

## Explicit non-authorization

Even if this QA pass is accepted, this artifact itself is not runtime metadata. It should be used to decide whether to authorize the graph-wide tagging pass using the v0.2.2 ontology and sparse instructions.
