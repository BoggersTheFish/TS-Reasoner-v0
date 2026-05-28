# v2.8.0: Training Loop Smoke

v2.8.0 proves that v2.7 verifier trace rows are usable supervised training signal.

The loop is deliberately small:

```text
verifier trace rows
→ tiny supervised status model
→ heldout stress split evaluation
→ compare against simple baselines
Command
python3 scripts/train_from_verifier_trace_smoke.py
Current metrics
{
  "train_accuracy": 1.0,
  "eval_accuracy": 1.0,
  "majority_baseline_eval_accuracy": 0.4286,
  "confidence_baseline_eval_accuracy": 0.5714,
  "learned_beats_majority_margin": 0.5714,
  "learned_beats_confidence_margin": 0.4286
}
Row split
row_count: 91
train_rows: 35
eval_rows: 56

The training split uses verifier-trace rows from the v2.6 eval split. The heldout eval split uses verifier-trace rows from the v2.6 stress split.

Boundary

This is a smoke-scale training loop, not a broad model-training claim.

The trained status model is not proof authority.
Typed verifier traces define target labels.
The model learns to predict verifier status from exported trace features.
No TensionLM runtime is loaded.
No neural language model is trained.
Future larger models must preserve verifier/model separation.
