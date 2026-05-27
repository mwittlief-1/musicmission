# Cartenza Affinity Tag Ontology v0.2.2 Amendments

## Decision

Approve v0.2.2 for sparse production-simulation tagging only. Do **not** approve runtime ingestion or graph-wide tagging.

## Ontology change

Add one canonical `emotion_theme` tag:

### `uplift`

**Definition:** A release-oriented, emotionally rising, aspirational, or cathartic positive turn that is not simply celebration, romance, nostalgia, or self-mythology.

**Use when:** The song’s central emotional motion is upward release, resilience, empowerment, or cathartic lift.

**Do not use when:** The song is merely upbeat, celebratory, romantic, nostalgic, devotional, or triumphal-persona focused.

**Aliases / analyst language:** hopeful_release, cathartic_release, aspirational_release, inspirational_lift, empowerment_release.

## Instruction hardening

- Default target is **5–8 tags per song**.
- 9–10 tags are allowed only when the song is genuinely multi-context, bridge-heavy, or routing-sensitive.
- Empty dimensions are allowed.
- Do not tag every dimension to satisfy shape.
- `safe_gateway` is not a default; use only when the song actively helps sequence into a route.
- `context_dependent` is not a default caution; use only when social/use-case context materially changes routing.
- Any alias leakage remains a hard QA failure.

## No change

The seven dimensions remain locked for this pilot:

```text
vocal_performance
emotion_theme
sonic_texture
rhythm_body
form_container
social_context
routing_caution
```
