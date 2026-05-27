# Waymark Fine-Tuning Strategy v0.1

## Recommendation

Do not pursue fine-tuning now.

The near-term Waymark risk is not primarily that the base model cannot learn Waymark style. The risk is whether a bounded mission-generation pipeline can reliably combine:

- Atlas digest;
- Taste Feature Registry;
- candidate pools;
- structured schema;
- evaluator and repair loop;
- model routing.

The model should act as the mission designer, not the whole taste brain.

## Why Defer

1. Fine-tuning platform availability and model lifecycle are not a reliable near-term foundation for this product path.
2. We do not yet have a large enough labeled corpus of high-quality mission examples.
3. Fine-tuning will not replace Atlas memory, candidate retrieval, catalog resolution, or the evidence model.
4. Current evidence suggests `gpt-5.4-mini` may already be good enough when bounded by strong context and candidate constraints.
5. Fine-tuning adds training cost, inference cost, evaluation burden, migration work, and retraining risk.
6. The cheaper and more flexible strategy for now is model routing plus structured context.

## Revisit Conditions

Reconsider fine-tuning only when one or more of these are true:

- We have 500+ high-quality mission-generation examples.
- We have 1,000+ labeled song/item to Taste Feature mappings.
- We see repeated product failures that prompting, evaluator repair, candidate constraints, and model routing cannot solve.
- We need lower-latency chip generation at scale.
- We need a stable style/classifier model for survey intake or note-to-feature extraction.
- OpenAI or another provider offers a stable fine-tuning path that fits Waymark's model, cost, and lifecycle needs.

## Possible Future Fine-Tune Targets

If revisited later, do not start with full mission generation.

Better candidates:

1. Note to Taste Feature extraction.
2. Survey answer to Atlas seed classification.
3. Chip label generation from canonical feature plus user vocabulary.
4. Reaction evidence to possible Atlas update candidate classification.
5. Mission output repair and guardrail correction.

Full mission-generation fine-tuning should be considered only after enough labeled examples exist and the structured pipeline is already working.

## Cost Risk

Training is not free and can become nontrivial depending on model and provider. Fine-tuned inference may cost more than base small-model inference. Fine-tuning also creates lifecycle risk from base model deprecations, migrations, evaluation drift, and retraining.

For now, structured context plus model routing is the better Waymark bet.

## Draft Routing Hypothesis

- Default full mission generation: `gpt-5.4-mini`
- Cheap/simple substeps to test: `gpt-5.4-nano`
- Hard mission fallback: `gpt-5.4`
- Quality ceiling / ambiguous high-value missions: `gpt-5.5`
- Legacy baseline: `gpt-4.1`

This is a hypothesis, not a locked product decision.
