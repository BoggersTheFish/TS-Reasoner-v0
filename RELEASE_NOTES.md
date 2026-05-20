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

## v0.3.0

v0.3.0 adds a learned candidate-proposal experiment while preserving the v0 JSON trace contract. Candidate chains remain verified by the existing CIG, tension-ranker, repair, and trace pipeline.

This is the first TS-Codex-guided TS-Reasoner release. TS-Codex-OS v0.1.0 inspected TS-Reasoner-v0 before merge and detected release-control tensions around verification receipts and stale artifacts; v0.3.0 closes those tensions with regenerated artifacts and release receipts.

Release scope:

- Learn which candidate-chain templates to propose from synthetic rows.
- Keep generated candidates inspectable as `ReasoningChain` objects.
- Pass all generated chains through the existing CIG checker, ranker, repairer, and JSON trace exporter.
- Add coverage metrics for candidate count, stable candidate inclusion, adversarial suppression, and contradiction-aware inclusion.
- Compare deterministic generator, learned generator, learned generator plus safety fallback, and random candidate proposer.
- Do not claim full LLM generation, open-ended reasoning generation, or robust natural-language reasoning.

Verification:

```bash
python3 -m unittest discover
python3 demo_reasoning.py
python3 inference.py --question "If all A are B and all B are C, are all A C?"
python3 scripts/build_synthetic_dataset.py
python3 scripts/train_learned_ranker.py
python3 scripts/compare_rankers.py
python3 scripts/train_candidate_generator.py
python3 scripts/evaluate_candidate_generators.py
PYTHONPATH=/home/boggersthefish/BoggersSpace/TS-Codex-OS python3 -m ts_codex_os.cli status --project-path .
```

Verification result:

- `15` unittest tests passed.
- Demo eval regenerated `artifacts/eval_summary.json` with `5/5` toy tasks matching expected behavior.
- CLI inference regenerated `artifacts/latest_trace.json` and returned `all A are C.` with global tension `0.0000`.
- Ranker artifacts and comparison artifacts were regenerated.
- Candidate-generator artifacts and coverage artifacts were regenerated.
- TS-Codex-OS v0.1.0 status reported `0` tensions after receipts were added.
- Release receipt: `artifacts/release_receipt_v0.3.0.json`.
- Artifact receipt: `artifacts/artifact_receipt_v0.3.0.json`.
