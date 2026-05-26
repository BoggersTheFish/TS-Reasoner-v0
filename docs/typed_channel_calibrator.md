# Learned Typed-Channel Calibrator

This branch tests one narrow question:

> Can TS-Reasoner learn channel activation, weighting, and resolver priority from typed traces without retraining the reasoning system from scratch?

The honest claim:

> This release tests whether TS-Reasoner can learn to activate and prioritize typed tension channels from trace-level supervision, rather than learning reasoning behaviour end-to-end.

## Scope

The calibrator is not a language model and not an end-to-end reasoner. It learns over existing typed-channel traces:

- channel activation
- channel weights
- resolver priority

The deterministic typed-channel resolvers remain the operational priors.

## Files

- `ts_reasoner/calibration/features.py`
- `ts_reasoner/calibration/calibrator.py`
- `ts_reasoner/calibration/train.py`
- `scripts/build_typed_calibrator_dataset.py`
- `scripts/train_typed_channel_calibrator.py`
- `scripts/evaluate_typed_channel_calibrator.py`
- `data/typed_channel_calibrator_dataset.jsonl`
- `artifacts/typed_channel_calibrator.json`
- `artifacts/typed_channel_calibrator_report.json`

## Run

```bash
python3 scripts/build_typed_calibrator_dataset.py
python3 scripts/train_typed_channel_calibrator.py
python3 scripts/evaluate_typed_channel_calibrator.py
```

## Ablations

The report compares:

- `hand_coded_baseline`
- `learned_activation`
- `learned_channel_weight`
- `learned_resolver_priority`
- `full_calibrator`

Metrics:

- `answer_accuracy`
- `channel_activation_accuracy`
- `resolver_accuracy`
- `reverse_fallacy_count`
- `identity_collapse_count`
- `unsupported_leap_count`
- `abstention_correctness`
- `trace_schema_validity`

## Non-Claims

- No TensionLM integration.
- No large-model training.
- No general reasoning claim.
- No claim that calibration replaces deterministic channels.

The research step is the training target shift: from behavior imitation to typed operational channel calibration.
