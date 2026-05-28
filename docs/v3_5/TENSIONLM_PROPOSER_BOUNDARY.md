# v3.5 TensionLM Proposer Boundary

v3.5 adds a TensionLM-shaped proposer boundary smoke.

This does not load TensionLM. It tests the contract that future TensionLM outputs must obey:

    TensionLM proposes language-shaped candidate claims.
    TS-Reasoner verifies typed proof support.
    Confidence is metadata, not proof.

## Gates

    verifier_selection_accuracy == 1.0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    live_tensionlm_runtime_loaded == false

## Why this matters

This protects the system from a dangerous failure mode:

    high-confidence unsupported candidate -> accepted because model sounded sure

v3.5 keeps that blocked.

## Claim boundary

This release does not claim live TensionLM runtime integration. It only tests the proposer/verifier contract using TensionLM-shaped exported candidate rows.
