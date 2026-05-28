# Scaled Learned vs Exported Candidate Comparison

TS-Reasoner v2.3 scales the learned-vs-exported comparison from the v2.2 seed set to a deterministic 15-case structured benchmark surface.

Each case contains:

- one valid low-confidence candidate
- high-confidence reverse candidate
- high-confidence contradiction candidate
- high-confidence identity-collapse candidate
- high-confidence unsupported candidate

The learned arm ranks candidates with the v2.0 learned candidate model. The exported baseline ranks by input/export confidence. Both arms are checked by the same typed verifier.

## Commands

    python3 scripts/build_scaled_comparison_set.py
    python3 scripts/evaluate_scaled_learned_vs_exported_candidate_comparison.py
    python3 -m unittest discover -q

## Current metrics

- case_count: 15
- learned_top_accept_rate: 1.0
- exported_confidence_top_accept_rate: 0.0
- learned_top_beats_exported_confidence_top_rate: 1.0
- exported_high_confidence_bad_block_rate: 1.0
- accepted_without_typed_support_count: 0
- candidate_graph_contamination_count: 0
- trace_schema_validity: 1.0

## Boundary

This is a shaped synthetic benchmark surface. It does not claim broad natural-language reasoning, live TensionLM integration, or general candidate-ranking superiority.

The claim is narrower: on this scaled structured comparison set, learned candidate ranking selects typed-supported candidates where exported-confidence ordering selects high-confidence bad candidates, and typed verification still prevents unsupported proof authority.
