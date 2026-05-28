# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-v2.1_adversarial_candidate_stress-blue)](MODEL_CARD.md)

TS-Reasoner is an inspectable reasoning control loop. It generates candidate
reasoning chains, scores local and global tension, runs a bounded repair or
compression loop, settles a trace, and exposes why a result was accepted or
rejected.

This repository is the stable public v2.1 foundation for that loop. It is not a
large language model, a general theorem prover, or a broad benchmark claim.

Current public bridge claim:

> TS-Reasoner can train a tiny learned candidate model that ranks/proposes
> structured candidate claims while typed channels remain the verifier,
> confidence remains metadata, and candidate graph contamination stays blocked.

## Typed Tension Channel Demo

The repo now includes a TS-Core-backed typed tension path alongside the existing public trace contract. The old fields remain, and traces also include:

```text
trace.tension_channels
trace.typed_runtime
```

Initial channels:

- `logic_transitivity`
- `identity_preservation`
- `directionality`
- `surface_structure`
- `confidence_abstention`
- `contradiction`
- `quantifier_scope`

Run the typed demo and benchmark:

```bash
python3 scripts/demo_typed_tension.py
python3 scripts/evaluate_typed_tension.py
```

Generated artifacts:

- `artifacts/typed_tension_demo.json`
- `artifacts/typed_tension_benchmark_report.json`
- `artifacts/typed_tension_receipt.json`

Claim level: demo. This shows specific failure modes separated into typed operational channels on small curated examples. It does not claim general reasoning.

### 10-Second Example

```text
All A are B.
All B are C.
Question: Are all A C?
```

The typed trace shows:

```text
logic_transitivity: infer A -> C
directionality: block C -> A
identity_preservation: block A = C
surface_structure: tag A -> C as inferred, not stated
```

That is the point of typed tension: proof completion, reverse-inference blocking, and identity preservation are separate inspectable operations, not one blended score.

## Learned Typed-Channel Calibrator

The next scoped experiment is a small calibrator over typed traces:

```bash
python3 scripts/build_typed_calibrator_dataset.py
python3 scripts/train_typed_channel_calibrator.py
python3 scripts/evaluate_typed_channel_calibrator.py
```

It compares hand-coded channel decisions against learned activation, learned channel weights, learned resolver priority, and the full calibrator. The research claim is narrow: training moves from learning reasoning end-to-end to calibrating typed operational channels. TensionLM is not part of this branch.

See `docs/typed_channel_calibrator.md`.

## Calibrator Generalization Stress

The stress evaluator checks whether the typed-channel calibrator survives heldout structure without retraining:

```bash
python3 scripts/evaluate_typed_channel_calibrator_stress.py
```

It covers variable renaming, deeper chains, distractors, quantifier traps, contradiction placement, reverse/identity adversarial queries, heldout relation shapes, and noisy surface forms. The point is credibility: the receipt should show clean generalization, expose partial limits, or catch overfit.

See `docs/typed_channel_calibrator_generalization_stress.md`.

## Calibration Progression

The current calibration arc is intentionally receipt-first:

- Scoped calibrator eval: `1.0` answer accuracy, channel activation accuracy, resolver accuracy, abstention correctness, and trace schema validity on the typed trace-supervision benchmark.
- Generalization stress: Outcome B. The calibrator handled variable renaming but exposed failures on deeper chains, distractor premises, quantifier traps, and contradiction placement.
- Structural repair: query-relevant graph features repaired the targeted stress failures on the current stress benchmark. Depth generalization and distractor robustness moved from `0.0` to `1.0`; quantifier trap failures and contradiction misses moved from `1` to `0`.
- Known limitation: this is still synthetic, parser-controlled, and not natural-language robust. TensionLM remains out of scope for this release path.

See `docs/typed_channel_calibrator_structural_features.md`.

## Typed-Channel Release Receipt

Generate the unified release receipt for the kernel -> channels -> calibrator -> stress -> repair arc:

```bash
python3 scripts/generate_typed_channel_release_receipt.py
```

This writes `artifacts/typed_channel_release_receipt.json`.

See `docs/typed_channel_release_receipt.md`.

## TensionLM Candidate Bridge

v1.1.0 adds a dependency-light candidate bridge contract:

```text
TensionLM proposes.
TS-Reasoner verifies.
Typed channels decide.
Receipts explain.
```

The bridge admits external language/model outputs as candidate graph claims,
then verifies them without inserting candidate claims into the proof-support
graph. High-confidence bad proposals cannot override typed verification.

Run the bridge demo, normal eval, and adversarial stress:

```bash
python3 scripts/demo_tensionlm_candidate_bridge.py
python3 scripts/evaluate_tensionlm_candidate_bridge.py
python3 scripts/evaluate_tensionlm_candidate_bridge_adversarial.py
```

Generated artifacts:

- `artifacts/tensionlm_candidate_bridge_demo.json`
- `artifacts/tensionlm_candidate_bridge_report.json`
- `artifacts/tensionlm_candidate_bridge_receipt.json`
- `artifacts/tensionlm_candidate_bridge_adversarial_report.json`
- `artifacts/tensionlm_candidate_bridge_adversarial_receipt.json`

See `docs/tensionlm_candidate_bridge.md`.

## Real TensionLM Candidate Adapter

v1.2.0 adds a JSONL adapter for real or exported TensionLM-style candidate
outputs. This adapter consumes exported candidate JSONL. It does not load or
train TensionLM, and model confidence does not get proof authority. It
normalizes exported candidates into the v1.1 bridge contract while TS-Reasoner
typed channels remain the verifier.

```text
TensionLM proposes.
Bridge normalizes.
TS-Reasoner verifies.
Typed channels decide.
```

Run the adapter smoke and receipt:

```bash
python3 scripts/run_real_tensionlm_candidate_adapter.py
python3 scripts/evaluate_real_tensionlm_candidate_adapter.py
```

Generated artifacts:

- `artifacts/real_tensionlm_candidate_adapter_smoke.json`
- `artifacts/real_tensionlm_candidate_adapter_report.json`
- `artifacts/real_tensionlm_candidate_adapter_receipt.json`

See `docs/real_tensionlm_candidate_adapter.md`.

## Messy Language Candidate Stress

v1.3.0 stresses exported candidate ingestion with messy language before any live
model-loading work. It covers paraphrases, partial claims, extra irrelevant
text, contradictory candidate sets, unsupported leaps, bad or missing
confidence, ambiguous relation wording, and multi-candidate outputs where the
wrong candidate has higher confidence.

Run the stress receipt:

```bash
python3 scripts/evaluate_messy_language_candidate_stress.py
```

Generated artifacts:

- `artifacts/messy_language_candidate_stress_report.json`
- `artifacts/messy_language_candidate_stress_receipt.json`

The boundary remains unchanged: model text is candidate data, confidence is not
proof, and TS-Reasoner typed channels remain the verifier.

See `docs/messy_language_candidate_stress.md`.

## Live TensionLM Export Smoke

v1.4.0 adds an exported-output smoke for TensionLM-style candidates. This is not
live model integration into the verifier. It produces/reads exported JSON
candidate data, feeds that data through the v1.3 adapter, and verifies
provenance, rejection, typed support, and zero graph contamination.

Run the export smoke and receipt:

```bash
python3 scripts/run_live_tensionlm_export_smoke.py
python3 scripts/evaluate_live_tensionlm_export_smoke.py
```

Generated artifacts:

- `artifacts/live_tensionlm_export_smoke.json`
- `artifacts/live_tensionlm_export_smoke_report.json`
- `artifacts/live_tensionlm_export_smoke_receipt.json`

Hard boundary: TensionLM-style outputs remain candidate data and never become
proof without typed-channel support.

See `docs/live_tensionlm_export_smoke.md`.

## Real Exported TensionLM Sample

v1.5.0 evaluates a real exported TensionLM-side sample through the existing
TS-Reasoner adapter. The sample is sourced from the TensionLM checkout artifact
`/home/boggersthefish/BoggersSpace/bozo/logs/eval/117m_transitivity_seed42.json`.

This does not load TensionLM inside TS-Reasoner and does not train anything.
Raw completions are preserved as candidate provenance; export-side normalized
claims are evaluated unchanged by TS-Reasoner typed channels.

Run the receipt:

```bash
python3 scripts/evaluate_real_exported_tensionlm_sample.py
```

Generated artifacts:

- `artifacts/real_exported_tensionlm_sample_report.json`
- `artifacts/real_exported_tensionlm_sample_receipt.json`

See `docs/real_exported_tensionlm_sample.md`.

## TensionLM Export Set Evaluation

v1.6.0 evaluates a small set of real exported TensionLM-side samples through the
same adapter boundary. The set preserves accepted, rejected, abstained, and
malformed cases instead of hiding failures.

This does not load TensionLM inside TS-Reasoner and does not train anything.
Candidate confidence remains metadata; typed channels remain the proof
authority; candidate edges do not enter proof support.

Run the export set receipt:

```bash
python3 scripts/evaluate_tensionlm_export_set.py
```

Generated artifacts:

- `artifacts/tensionlm_export_set_report.json`
- `artifacts/tensionlm_export_set_receipt.json`

See `docs/tensionlm_export_set_evaluation.md`.

## Deeper-Chain Support Repair

v1.7.0 repairs the deeper-chain current-limit case preserved by the v1.6.0
export set receipt. A -> B -> C -> D style support is accepted inside the
existing typed verifier boundary, while wrong reverse candidates remain blocked.

Hard boundary remains unchanged: no TensionLM loading, no training, no
confidence-as-proof, and no candidate edges entering proof support.

Run the repair receipt:

```bash
python3 scripts/evaluate_deeper_chain_support_repair.py
```

Generated artifacts:

- `artifacts/deeper_chain_support_repair_report.json`
- `artifacts/deeper_chain_support_repair_receipt.json`

See `docs/deeper_chain_support_repair.md`.

## Learned Candidate Model

v2.0.0 adds a dependency-light learned candidate model before the typed
verifier. The model trains on controlled structured reasoning examples and
predicts candidate ranking, channel activations, resolver labels, and
accept/reject/abstain status.

The boundary remains unchanged:

```text
learned model proposes/ranks
-> candidate bridge
-> TS-Reasoner typed channels verify
-> receipts explain accepted, rejected, and abstained candidates
```

The learned model is not proof authority. Candidate confidence is metadata, and
accepted outputs require typed-channel support.

Run the full v2.0 receipt:

```bash
python3 scripts/build_learned_candidate_dataset.py
python3 scripts/train_learned_candidate_model.py
python3 scripts/evaluate_learned_candidate_model.py
python3 scripts/demo_learned_candidate_model.py
```

Generated artifacts:

- `artifacts/learned_candidate_model.json`
- `artifacts/learned_candidate_model_report.json`
- `artifacts/learned_candidate_model_stress_report.json`
- `artifacts/learned_candidate_model_receipt.json`
- `artifacts/learned_candidate_model_demo.json`

See `docs/learned_candidate_model.md`.

## One-Command Run

```bash
python3 inference.py --question "If all A are B and all B are C, are all A C?"
```

That writes `artifacts/latest_trace.json` and prints the selected answer,
selected chain, and global tension.

Run all examples and tests:

```bash
python3 demo_reasoning.py
python3 -m unittest discover
```

## What It Does

The core pipeline is:

```text
input problem
-> candidate chains
-> Claim-Interaction Graph checks
-> local/global tension scoring
-> bounded repair/compression loop
-> selected answer or failure reason
-> JSON trace
```

Tension is a transparent instability score. Local tension marks the step where
support is missing, a contradiction appears, a quantifier jump happens, or a
claim is overconfident. Global tension summarizes the candidate chain.

Traces are the public API of TS reasoning. Every trace records the input,
candidate steps, local tension, global tension, chosen action, rejected
alternatives, settled answer, and failure reason when the loop does not settle.

## v1.0 Receipts

Generate the stable v1 benchmark receipt:

```bash
python3 scripts/evaluate_v1_baseline.py
```

This writes:

- `artifacts/v1_baseline_report.json`
- `artifacts/release_receipt_v1.0.0.json`

Current v1 receipt:

- `20` tasks total.
- `16` expected-pass tasks.
- `4` adversarial known-limit tasks.
- `full_control_loop`: `16/16` on expected-pass tasks.
- Known-limit tasks are included to make failures visible, not to claim solved behavior.

See `BENCHMARKS.md` for the benchmark categories and `LIMITATIONS.md` for the
non-claims.

## TensionLM Bridge

TS-Reasoner can use TensionLM as an optional candidate proposer while keeping
TS-Reasoner as the verifier:

```text
problem
-> TS-Reasoner reasoning state
-> TensionLM proposes candidate text
-> tension scorer and verifier evaluate it
-> trace records acceptance, repair, or rejection
```

Run the offline bridge smoke receipt:

```bash
python3 scripts/run_tensionlm_bridge.py --offline
```

Run against a local public TensionLM checkout:

```bash
python3 scripts/run_tensionlm_bridge.py --tensionlm-path ../TensionLM
```

The bridge writes `artifacts/tensionlm_bridge_smoke.json`. The public claim is
narrow: this tests whether a tension-attention language model can improve an
inspectable reasoning loop.

## TensionProofLM Target

The next model target is `TensionProofLM-22M`: a small model trained for proof
step proposal, repair, and abstention, not general chat.

Run the tiny smoke-training/eval receipt:

```bash
python3 scripts/run_tensionprooflm_smoke.py
```

This writes `artifacts/tensionprooflm_smoke_report.json`. The smoke run validates
the data/eval contract only; it is not a trained 22M checkpoint.

## Public Docs

- `TRACE_SCHEMA.md`: stable JSON trace contract.
- `BENCHMARKS.md`: v1 benchmark suite and receipt shape.
- `LIMITATIONS.md`: explicit known limits and non-claims.
- `MODEL_CARD.md`: intended use, risks, and eval summary.
- `docs/tensionlm_bridge.md`: optional TensionLM proposal bridge.
- `docs/tensionprooflm_22m.md`: next model target and metric.

## Installation

No runtime dependencies are required beyond Python 3.10+.

```bash
python3 -m unittest discover
python3 inference.py --question "If all cats are mammals and all mammals are animals, are all cats animals?"
```

The package also exposes a console entry point when installed:

```bash
ts-reasoner --question "If all A are B and all B are C, are all A C?"
```

## Claim Boundary

TS-Reasoner v2.0 claims:

- stable inspectable traces,
- deterministic small reasoning receipts,
- visible failure modes,
- a bridge contract for learned candidate proposers,
- real exported TensionLM-side candidate sets can cross into TS-Reasoner as candidate data,
- a tiny learned model can rank/propose structured candidate claims and predict typed-channel signals,
- typed channels remain the proof authority,
- malformed and current-limit cases are preserved as receipt evidence,
- candidate graph contamination remains blocked.

TS-Reasoner v2.0 does not claim:

- general reasoning ability,
- production decision-making reliability,
- formal proof completeness,
- chatbot quality,
- superiority over frontier models,
- live TensionLM integration into the verifier,
- model confidence as proof authority.

## v2.1.0: Learned Candidate Model Adversarial Stress

v2.1.0 adds an adversarial stress layer for the v2.0 learned candidate model.

The learned model remains advisory. It can rank and score candidate claims, but typed verifier channels remain the only proof authority.

Adversarial cases include:

- high-confidence wrong candidates
- malformed outputs with fake confidence
- unsupported plausible claims
- reverse inference traps
- contradiction traps
- identity-collapse traps
- distractor-heavy premise sets
- missing-provenance candidates

Core v2.1 boundary result:

- candidate_graph_contamination_count: 0
- accepted_without_typed_support_count: 0
- high_confidence_bad_block_rate: 1.0
- high_confidence_bad_total: 13
- unsupported_abstained_count: 6
- trace_schema_validity: 1.0

Some bad candidates are blocked by abstention rather than hard rejection. That is intentional: abstention is safer than pretending unsupported claims are decidable.

Run:

```bash
python3 scripts/evaluate_learned_candidate_model_adversarial.py
python3 -m unittest discover -q

## v2.2.0: Learned vs Exported Candidate Comparison

v2.2.0 compares learned candidate ranking against exported-candidate confidence ordering on the same structured adversarial candidate cases.

Core result:

- learned_top_accept_rate: 0.8571
- exported_confidence_top_accept_rate: 0.1429
- learned_top_beats_exported_confidence_top_rate: 0.7143
- accepted_without_typed_support_count: 0
- candidate_graph_contamination_count: 0
- trace_schema_validity: 1.0

Run:

    python3 scripts/evaluate_learned_vs_exported_candidate_comparison.py
    python3 -m unittest discover -q

See `docs/learned_vs_exported_candidate_comparison.md`.

