# v2.9.0: Active Learning Loop

v2.9.0 adds a smoke-scale active-learning loop on top of the v2.7/v2.8 verifier-trace training stack.

The loop is:

```text
holdout verifier trace rows
→ create challenge rows
→ baseline model underperforms
→ add verifier-labeled challenge rows
→ retrain
→ measure improvement
```

## Command

```bash
python3 scripts/run_active_learning_loop_v29.py
```

## Current metrics

```json
{
  "baseline_challenge_accuracy": 0.6667,
  "active_learning_challenge_accuracy": 1.0,
  "active_learning_improvement": 0.3333,
  "confidence_baseline_challenge_accuracy": 0.3333,
  "active_beats_confidence_margin": 0.6667
}
```

## Row counts

```text
row_count: 91
base_train_rows: 35
challenge_rows: 12
augmented_train_rows: 47
```

## Generated artifacts

```text
data/active_learning_challenge_v29.jsonl
data/active_learning_augmented_training_v29.jsonl
artifacts/active_learning_status_model_v29.json
artifacts/active_learning_loop_v29_report.json
artifacts/active_learning_loop_v29_receipt.json
```

## Boundary

This is a smoke-scale active-learning loop, not a broad model-training claim.

- The trained model is not proof authority.
- Typed verifier traces define target labels.
- Challenge labels are verifier-derived.
- No TensionLM runtime is loaded.
- No neural language model is trained.
- v2.9 demonstrates the loop shape before v3.0 flagship model work.
