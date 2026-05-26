# Release Notes

## Typed-Channel Release Receipt

This release-receipt branch summarizes the full TS-Reasoner typed-channel arc:

```text
TS-Core-backed typed channels
-> learned typed-channel calibrator
-> generalization stress
-> structural feature repair
```

Generated artifact:

- `artifacts/typed_channel_release_receipt.json`

Verification:

```bash
python3 -m unittest discover
python3 scripts/generate_typed_channel_release_receipt.py
```

Claim level: experimental. The public story is that TS-Reasoner now has TS-Core-backed typed tension channels plus a learned calibrator; stress testing exposed structural generalization failures, and query-relevant graph features repaired those failures on the current stress benchmark.

## Structural Feature Repair for Typed-Channel Calibration

This release tests whether the calibrator failures exposed by generalization stress are structural-feature gaps rather than failures of the typed-channel approach.

Core change:

- Add query-relevant graph features for path length, distractor ratio, quantifier signatures, contradiction placement, and candidate operation requirements.
- Preserve the original generalization stress report as the failure receipt.
- Add a repaired stress evaluator comparing `original_calibrator`, `+ path features`, `+ distractor features`, `+ quantifier features`, `+ contradiction-placement features`, and `full_structural_features`.

Generated artifacts:

- `artifacts/typed_channel_calibrator_structural_features_report.json`
- `artifacts/typed_channel_calibrator_structural_features_receipt.json`

Verification:

```bash
python3 -m unittest discover
python3 scripts/evaluate_typed_channel_calibrator_structural_features.py
```

Claim level: experimental. The result supports targeted structural repair, not broad reasoning generalization. TensionLM remains out of scope.

## Typed-Channel Calibrator Generalization Stress

This release tests whether the typed-channel calibrator generalizes beyond the exact trace surface it was trained on.

Stress cases include variable renaming, deeper chains, distractor premises, quantifier traps, contradiction placement, reverse/identity adversarial queries, heldout relation shapes, and noisy surface forms.

Generated artifacts:

- `data/typed_channel_calibrator_stress.jsonl`
- `artifacts/typed_channel_calibrator_stress_report.json`
- `artifacts/typed_channel_calibrator_stress_receipt.json`

Verification:

```bash
python3 -m unittest discover
python3 scripts/evaluate_typed_channel_calibrator_stress.py
```

Honest outcomes are explicit: clean generalization, partial generalization with depth/feature limits, or overfit detected by receipt. TensionLM remains out of scope.

## Learned Typed-Channel Calibrator

This release tests whether TS-Reasoner can learn to activate and prioritize typed tension channels from trace-level supervision, rather than learning reasoning behaviour end-to-end.

Core change:

- Add a tiny dependency-light calibrator for typed-channel activation, channel weights, and resolver priority.
- Build channel-level training rows from existing typed tension benchmark/demo traces.
- Compare `hand_coded_baseline`, `learned_activation`, `learned_channel_weight`, `learned_resolver_priority`, and `full_calibrator`.
- Preserve the existing public trace schema; the calibrator is an evaluation artifact, not a replacement for deterministic resolvers.

Generated artifacts:

- `data/typed_channel_calibrator_dataset.jsonl`
- `artifacts/typed_channel_calibrator.json`
- `artifacts/typed_channel_calibrator_report.json`
- `artifacts/typed_channel_calibrator_receipt.json`

Verification:

```bash
python3 -m unittest discover
python3 scripts/build_typed_calibrator_dataset.py
python3 scripts/train_typed_channel_calibrator.py
python3 scripts/evaluate_typed_channel_calibrator.py
```

Claim level: experimental. The research step is the training-target shift: from behavior imitation to typed operational channel calibration. No TensionLM bridge or large-model training is included.

## Typed Tension Traces: TS-Core-backed channel reasoning

This release adds TS-Core-backed typed tension traces while preserving the existing TS-Reasoner public trace contract.

Core change:

- The system now emits per-channel reasoning traces, showing which typed tensions activated, how they resolved, and whether the answer settled.

Included channels:

- `logic_transitivity`
- `identity_preservation`
- `directionality`
- `surface_structure`
- `confidence_abstention`
- `contradiction`
- `quantifier_scope`

Generated artifacts:

- `artifacts/typed_tension_demo.json`
- `artifacts/typed_tension_benchmark_report.json`
- `artifacts/typed_tension_receipt.json`

Verification:

```bash
python3 -m unittest discover
python3 scripts/demo_typed_tension.py
python3 scripts/evaluate_typed_tension.py
```

Claim level: demo. This release separates specific reasoning failure modes into typed operational channels on small curated examples. It does not claim general reasoning, theorem proving, or broad natural-language robustness.

## v1.0.0

v1.0.0 is the stable public trace-contract release. It keeps the same
inspectable output schema, adds focused public docs, adds adversarial
known-limit cases, and runs tests in GitHub Actions.

Release scope:

- Freeze and document the public JSON output shape in `TRACE_SCHEMA.md`.
- Document the v1 benchmark receipt in `BENCHMARKS.md`.
- Document explicit non-claims and known failures in `LIMITATIONS.md`.
- Add `data/external_benchmark_v1.jsonl` with expected passes and known limits.
- Add `scripts/evaluate_v1_baseline.py`.
- Add optional `TS-Reasoner + TensionLM` bridge tooling.
- Add a tiny `TensionProofLM-22M` target smoke-training/eval receipt.
- Add CI via `.github/workflows/tests.yml`.

Verification:

```bash
python3 -m unittest discover
python3 scripts/evaluate_v1_baseline.py
python3 scripts/run_tensionlm_bridge.py --offline
python3 scripts/run_tensionprooflm_smoke.py
```

The release claim is narrow: this is stable enough for another technical reader
to inspect or build on. It is not a broad reasoning benchmark or large model.

## v0.9.0

v0.9.0 closes the narrow proof-chain gap exposed by v0.8. The release adds
explicit positive universal bridge support for small transitive `all/all`
chains while keeping the v0.8 benchmark fixture shape stable.

Release scope:

- Add shared transitive proof-chain support for normalized `all A are B` chains.
- Use that support in candidate generation, CIG support checks, and tension ranking.
- Add `scripts/evaluate_v09_proof_chains.py`.
- Generate `artifacts/v09_proof_chain_report.json`.
- Add `docs/v09_proof_chain_support.md`.

Verification:

```bash
python3 -m unittest discover
python3 scripts/evaluate_v09_proof_chains.py
```

Verification result:

- `27` unittest tests passed.
- v0.9 benchmark ran the same `10` externalized small-reasoning tasks.
- `full_control_loop`: `10/10` correct, `10/10` settled, mean global tension `0.0`.
- `small_proof_chain/full_control_loop`: `2/2` correct.
- Remaining limit: positive universal chains only; still toy-scope and normalized.

## v0.8.0

v0.8.0 adds the first externalized small benchmark harness. It turns the v0.7
bounded control loop into a repeatable baseline comparison over curated
external-style tasks normalized into TS-Reasoner relation form.

Release scope:

- Add `data/external_benchmark_v08.jsonl` with ten tasks across five categories.
- Add `ts_reasoner.benchmark` with loader, scorer, runner, and baseline summaries.
- Add `scripts/evaluate_v08_external_benchmark.py`.
- Generate `artifacts/v08_external_benchmark_report.json`.
- Add `docs/v08_external_benchmark_harness.md`.
- Add benchmark regression tests.

Verification:

```bash
python3 -m unittest discover
python3 scripts/evaluate_v08_external_benchmark.py
```

Verification result:

- `26` unittest tests passed.
- v0.8 benchmark ran `10` externalized small-reasoning tasks.
- `direct`: `4/10` correct, mean global tension `0.2141`.
- `random_selector`: `5/10` correct, mean global tension `0.1771`.
- `ranker_only`: `8/10` correct, mean global tension `0.0767`.
- `full_control_loop`: `8/10` correct, `10/10` settled, mean global tension `0.0`.
- Known gap: `full_control_loop` fails both `small_proof_chain` tasks by settling
  to low-tension abstentions.

This is a toy-scope receipt, not a broad benchmark claim.

## v0.7.0

v0.7.0 closes the residual no-compression failure exposed by v0.6. Compression
now removes redundant non-premise claims that are already represented by earlier
graph claims, allowing contradiction repair traces to settle instead of stopping
with `no_compression_available`.

Release scope:

- Extend `COMPRESS_TRACE` to remove redundant non-premise claims.
- Preserve exact-duplicate compression behavior.
- Add `scripts/evaluate_v07_loop.py`.
- Generate `artifacts/v07_loop_eval.json`.
- Add a regression test for the contradiction-forced-answer closure path.

Verification:

```bash
python3 -m unittest discover
python3 scripts/evaluate_v07_loop.py
```

Verification result:

- `23` unittest tests passed.
- v0.7 loop eval ran `4` hard cases.
- `4/4` hard cases settled.
- Mean global tension dropped from `0.4552` to `0.0`.

## v0.6.0

v0.6.0 replaces one-shot candidate operation routing with a bounded multi-step
tension-control loop. Each candidate can now cycle through tension evaluation,
operation routing, state transition, verifier rescore, and residual logging
until it settles or reaches a bounded stop condition.

Release scope:

- Add `OperationRouter.run_until_stable(max_steps=5)`.
- Keep `run_once()` for v0.4/v0.5 compatibility.
- Add cycle-level operation traces.
- Add concrete handlers for accept, repair, compression, localization, and goal
  verification.
- Add harder v0.6 loop cases requiring repeated transitions.
- Add `scripts/evaluate_v06_loop.py`.
- Generate `artifacts/v06_loop_eval.json`.

Verification:

```bash
python3 -m unittest discover
python3 scripts/evaluate_v06_loop.py
```

Verification result:

- `22` unittest tests passed.
- v0.6 loop eval ran `4` hard cases.
- `3/4` hard cases settled.
- Mean global tension dropped from `0.4552` to `0.0`.
- One failed-to-settle case remains: `v06_contradiction_forced_answer`.

## v0.5.0

v0.5.0 adds a residual-trained coupling matrix. The learner replays v0.4
candidate repair transitions, measures before/after coordinated tension drops,
and trains channel-to-channel coupling weights from successful repairs.

Release scope:

- Add `train_residual_coupling_matrix()`.
- Add `scripts/train_coupling_matrix.py`.
- Add learned matrix loading through `TensionCoordinator.from_json()`.
- Add CLI support via `--coupling-matrix`.
- Generate `artifacts/learned_coupling_matrix_v05.json`.
- Generate `artifacts/learned_coupling_matrix_summary.json`.

Verification:

```bash
python3 -m unittest discover
python3 scripts/train_coupling_matrix.py
python3 inference.py --question "If some A are B and all B are C, are all A C?" --premise "Some A are B." --premise "All B are C." --coupling-matrix artifacts/learned_coupling_matrix_v05.json --trace /tmp/ts-reasoner-v05-trace.json
```

Verification result:

- `21` unittest tests passed.
- Coupling learner trained on `168` candidates with `126` successful repair examples.
- CLI loaded the learned matrix and preserved the repaired direct-candidate transition.

## v0.4.0

v0.4.0 adds the coordinated tension-state repair loop. The pipeline now runs
specialist tension agents over each candidate chain, propagates their signals
through a coupling matrix, routes one bounded operation, applies a repair when
available, and records before/after residuals in the JSON trace.

Release scope:

- Add `logic`, `goal`, `repair`, and `compression` tension agents.
- Add an explicit coupling matrix and coordinated tension field.
- Add `OperationRouter` for one-step closed-loop candidate repair.
- Accept repaired candidate states only when global tension does not increase.
- Preserve top-level v0 trace fields while adding operation-loop telemetry.
- Extend the toy CIG verifier so existential bridge repairs can settle:
  `some A are B` plus `all B are C` supports `some A are C`.

Verification:

```bash
python3 -m unittest discover
```

Verification result:

- `19` unittest tests passed.
- Release receipt: `artifacts/release_receipt_v0.4.0.json`.

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
