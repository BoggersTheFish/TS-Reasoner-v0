# Typed-Channel Release Receipt

This release receipt ties the current typed-channel stack into one public claim surface:

```text
TS-Core-backed typed channels
-> learned typed-channel calibrator
-> heldout generalization stress
-> structural feature repair
```

Generate it with:

```bash
python3 scripts/generate_typed_channel_release_receipt.py
```

Generated artifact:

- `artifacts/typed_channel_release_receipt.json`

## Public Story

TS-Reasoner now has TS-Core-backed typed tension channels plus a learned calibrator. Stress testing exposed structural generalization failures, and query-relevant graph features repaired those failures on the current stress benchmark.

## Evidence Chain

- Typed channels: `artifacts/typed_tension_benchmark_report.json`
- Scoped calibrator: `artifacts/typed_channel_calibrator_report.json`
- Generalization stress: `artifacts/typed_channel_calibrator_stress_report.json`
- Structural repair: `artifacts/typed_channel_calibrator_structural_features_report.json`

## Current Receipt Summary

```text
Scoped calibrator:
  answer_accuracy: 1.0
  channel_activation_accuracy: 1.0
  resolver_accuracy: 1.0
  abstention_correctness: 1.0
  trace_schema_validity: 1.0

Generalization stress:
  outcome: Outcome B
  depth_generalization_accuracy: 0.0
  distractor_robustness: 0.0
  quantifier_trap_failure_count: 1
  contradiction_miss_count: 1

Structural repair:
  depth_generalization: 1.0
  distractor_robustness: 1.0
  quantifier_trap_failures: 0
  contradiction_misses: 0
  trace_schema_validity: 1.0
```

## Non-Claims

- This is not broad reasoning generalization.
- This is not natural-language robustness.
- This is not a TensionLM bridge.
- This is not end-to-end learned reasoning.

Claim level: experimental.
