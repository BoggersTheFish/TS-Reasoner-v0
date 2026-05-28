# Learned vs Exported Candidate Comparison

TS-Reasoner v2.2 compares two candidate-ordering policies on the same structured adversarial candidate cases:

1. learned candidate model ranking
2. exported-candidate confidence ordering

Typed verification remains the proof authority for both arms.

## Question

When the same candidate set contains valid low-confidence candidates and bad high-confidence candidates, does the learned candidate model rank the typed-supported candidate above the exported-confidence baseline?

## Command

```bash
python3 scripts/evaluate_learned_vs_exported_candidate_comparison.py
python3 -m unittest discover -q
Current metrics
learned_top_accept_rate: 0.8571
exported_confidence_top_accept_rate: 0.1429
learned_top_beats_exported_confidence_top_rate: 0.7143
same_top_candidate_rate: 0.0
exported_high_confidence_bad_block_rate: 0.9286
accepted_without_typed_support_count: 0
candidate_graph_contamination_count: 0
trace_schema_validity: 1.0
Boundary

This is not a broad natural-language benchmark and does not load a live TensionLM runtime.

The exported arm is a confidence-ordering baseline run through the existing export adapter. The learned arm is the v2.0 tiny learned candidate model. Both arms are checked by the same typed verifier.

The core claim is narrow:

on the same structured adversarial candidate cases, learned candidate ranking selects typed-supported candidates more often than exported confidence ordering, while typed verification remains proof authority.
