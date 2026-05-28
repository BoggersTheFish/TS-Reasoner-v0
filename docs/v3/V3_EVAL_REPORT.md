# TS-Reasoner v3.0 Evaluation Report

## Evaluation command

```bash
python3 scripts/v3/build_v3_training_dataset.py
python3 scripts/v3/train_v3_verifier_guided_model.py
python3 scripts/v3/evaluate_v3_verifier_guided_model.py
```

## Dataset

```text
raw_row_count: 150
row_count_after_dedupe: 103
duplicate_removed_count: 47
train_rows: 47
eval_rows: 56
active_challenge_rows: 12
```

## Metrics

```json
{
  "status_accuracy": 1.0,
  "channel_prediction_accuracy": 0.9888,
  "majority_baseline_accuracy": 0.4286,
  "confidence_baseline_accuracy": 0.5714,
  "beats_majority_margin": 0.5714,
  "beats_confidence_margin": 0.4286,
  "accepted_without_typed_support_count": 0,
  "candidate_graph_contamination_count": 0,
  "trace_schema_validity": 1.0
}
```

## Gates

All configured v3 release gates pass in the current report.

## Interpretation

The v3 model learns a bounded candidate-status/channel mapping from verifier-derived data and beats simple majority/confidence baselines on heldout stress rows.

This supports a bounded flagship model claim. It does not support a broad reasoning or general NLP claim.
