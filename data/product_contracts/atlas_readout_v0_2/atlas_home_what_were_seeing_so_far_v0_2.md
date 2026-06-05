# Atlas Home: What We're Seeing So Far v0.2

## Purpose

This module gives the user a compact first readout after Survey intake. It should surface what Cartenza is beginning to notice about the map without recapping the survey or presenting final taste truth.

The readout should show the strongest insights, not merely the largest counts. High-volume signals should lead when they are genuinely strongest, but they must not suppress sparse, coherent, clean positive pockets that are useful to test.

It should feel like:

```text
Cartenza is noticing the early shape of the map.
```

It should not feel like:

```text
Here is a report of the survey items you selected.
```

## Product Principle

Lead with interpretation. Support with evidence. Do not lead with evidence.

Show the strongest insights, not merely the biggest clusters.

## Required UI Shape

1. One short opening insight.
2. Four to five insight cards.
3. At least one card may surface a sparse-but-clean signal when the evidence is coherent.
4. One card should carry uncertainty, context-dependence, or boundary language.
5. Optional "what this sets up" line only when consuming Mission-team-provided metadata.

## Recommended Card Taxonomy

- Strongest Center
- Sound Shape
- Secondary Branch
- Sparse but Clean Signal
- Open Question / Boundary

## Length Limits

- Opening: max 35 words.
- Insight card title: max 8 words.
- Insight card body: max 35-45 words.
- Evidence examples: max 3 visible examples per card.
- Total module: target 220-360 words.
- Total module absolute max: 425 words.

## Sparse-Signal Rule

Surface a sparse-but-clean card when a region or archetype has:

- At least two positive examples.
- No negative examples.
- No ok/fine examples, or only weak or ambiguous neutral evidence.
- Meaningful graph coherence.
- Useful mission-testing value.

Use language such as:

- "small but clean signal"
- "worth testing"
- "needs more evidence"
- "not enough to call a center yet"

Do not say that a sparse pocket is a major region. Do not let a high-volume cluster bury it.

For the synthetic v0.2 fixture, classic/heavy rock is represented as a sparse-but-clean pocket: a compact body-and-scale signal that needs more evidence before Cartenza can call it a region.

## Tone

- Concise.
- Interpretive.
- Warm but not chatty.
- Careful, not overconfident.
- Product UI copy, not a report.
- No internal tags.
- No long explanation paragraphs.
- Curious about sparse signals without overstating them.

## Forbidden Copy Patterns

- "Out of 84 survey responses..."
- "You selected..."
- "You clicked..."
- "Your responses included..."
- "The cluster is backed by..."
- Raw tags such as `sonic_texture:guitar_forward`.
- Long artist or album inventory lists.
- "final map"
- "final truth"
- "we know"
- "you love"
- "Cartenza learned"
- Permanent rejection language.

## Allowed Copy Patterns

- "early signal"
- "strongest shape"
- "seems to"
- "worth testing"
- "open question"
- "boundary signal"
- "still unresolved"
- "the map is starting to see..."

## Evidence Rules

Evidence may appear as compact support under a card, but it must not dominate the card.

Use:

```text
Evidence: Nirvana, Pixies, Weezer
```

Do not use:

```text
The cluster is backed by names like Nirvana, Soundgarden, Pearl Jam, Alice in Chains, and Smashing Pumpkins...
```

## Fixture Status

The v0.2 fixture is synthetic and non-runtime. It does not use Matt-specific or founder-specific data, and it does not call OpenAI at runtime.

The fixture intentionally omits the optional mission setup line because no Mission-team-provided metadata is consumed in this slice.

The fixture includes a non-rendered `sparse_signal_debug` section. App UI must render only the `display_model`; tests and product review reports may use the debug section to verify sparse-card eligibility.
