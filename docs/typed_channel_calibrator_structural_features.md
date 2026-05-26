# Structural Feature Repair for Typed-Channel Calibration

This release tests whether the calibrator failures exposed by generalization stress are structural-feature gaps rather than failures of the typed-channel approach.

The previous stress report is intentionally preserved:

- `artifacts/typed_channel_calibrator_stress_report.json`
- `artifacts/typed_channel_calibrator_stress_receipt.json`

That report showed the calibrator handled variable renaming but failed on depth, distractors, quantifier traps, and contradiction placement.

## Added Features

The calibrator feature extractor now emits query-relevant graph features:

- query fields: `query_subject`, `query_object`, `query_relation`
- path fields: `shortest_path_exists`, `shortest_path_length`, `num_paths_between_query_nodes`, `has_direct_edge`, `has_inferred_edge`, `has_reverse_edge`, `reverse_path_exists`
- distractor fields: `query_relevant_edge_count`, `distractor_edge_count`, `distractor_ratio`
- quantifier fields: `path_quantifier_signature`, `path_contains_some`, `path_contains_no`, `path_all_subset_chain_valid`
- contradiction fields: `contradiction_on_query_path`, `contradiction_off_query_path`, `contradiction_blocks_answer`
- candidate-operation fields: `candidate_requires_transitive_closure`, `candidate_requires_reverse_inference`, `candidate_requires_identity_collapse`, `candidate_requires_quantifier_upgrade`

The highest-value repair features are:

- `shortest_path_length`
- `distractor_ratio`
- `path_quantifier_signature`
- `contradiction_on_query_path`
- `candidate_requires_quantifier_upgrade`

## Run

```bash
python3 scripts/evaluate_typed_channel_calibrator_structural_features.py
```

Generated artifacts:

- `artifacts/typed_channel_calibrator_structural_features_report.json`
- `artifacts/typed_channel_calibrator_structural_features_receipt.json`

## Ablations

The evaluator compares:

- `original_calibrator`
- `+ path features`
- `+ distractor features`
- `+ quantifier features`
- `+ contradiction-placement features`
- `full_structural_features`

## Latest Result

```text
original_calibrator:
  depth_generalization: 0.0
  distractor_robustness: 0.0
  quantifier_trap_failures: 1
  contradiction_misses: 1
  trace_schema_validity: 1.0

full_structural_features:
  depth_generalization: 1.0
  distractor_robustness: 1.0
  quantifier_trap_failures: 0
  contradiction_misses: 0
  trace_schema_validity: 1.0
```

This does not claim broad reasoning generalization. It shows targeted structural repair on the heldout stress surface while preserving the trace schema.

TensionLM remains out of scope.
