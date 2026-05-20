# Release Notes

## v0.1.0

TS-Reasoner-v0 is the first public proof-of-concept release of the inspectable TS reasoning telemetry pipeline.

This release includes a deterministic standard-library reasoner that maps `question -> candidate chains -> CIG checks -> tension issues -> repair suggestions -> selected low-tension answer -> JSON trace`. It is intentionally not a trained model or benchmark claim; v0 establishes the trace contract and hand-coded tension field that future learned rankers and generators can plug into.

Included:

- Deterministic candidate-chain generation.
- Claim-Interaction Graph extraction with provenance.
- Heuristic local/global tension scoring.
- Traceable repair suggestions.
- CLI, demo script, examples, tests, generated artifacts, model card, and MIT license.

## v1-learned-ranker draft

v1 adds the first learned tension-ranker while preserving the v0 JSON trace schema. On synthetic heldout reasoning tasks, the learned ranker matches or improves answer-quality scoring over the heuristic baseline, with ablations showing which trace features carry the signal. Because all learned ablations reach 1.0 on the current heldout set, this should be read as a schema-preserving learned-ranker smoke test, not evidence of robust general reasoning ability.

Added before merging v1:

- Adversarial synthetic cases where confident surface wording masks wrong logic.
- Heldout template families: symbolic A/B/C-style training, natural-term evaluation.
- Ablation table comparing heuristic ranker, learned ranker, learned without CIG features, learned without issue-kind features, and random baseline.

## v0.3.0-learned-candidate-generator draft

v0.3.0 adds learned candidate proposal while preserving inspectable CIG/tension/repair verification.

Draft scope:

- Learn which candidate-chain templates to propose from synthetic rows.
- Keep generated candidates inspectable as `ReasoningChain` objects.
- Pass all generated chains through the existing CIG checker, ranker, repairer, and JSON trace exporter.
- Do not claim full LLM generation or robust natural-language reasoning.
