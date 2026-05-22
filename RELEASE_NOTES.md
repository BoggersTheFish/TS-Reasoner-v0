# Release Notes

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
