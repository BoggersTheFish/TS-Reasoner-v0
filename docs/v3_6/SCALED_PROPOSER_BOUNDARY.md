# v3.6 Scaled Proposer Boundary Evaluation

v3.6 scales the v3.5 TensionLM-shaped proposer boundary from a tiny smoke test into a broader adversarial candidate-proposal evaluation.

## Core claim

    LLM/TensionLM-shaped candidates may be high-confidence, fluent, or wrong.
    TS-Reasoner only accepts typed-supported claims.

## Scope

This release tests candidate pressure against the proof boundary:

- high-confidence wrong candidates;
- reverse inference traps;
- identity-collapse traps;
- unsupported leaps;
- distractor-heavy premises;
- malformed candidate text;
- partial candidate text;
- abstention-required cases;
- multiple candidates where confidence points at the wrong answer.

## Gates

    wrong_accept_count == 0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    trace_schema_validity == 1.0
    live_tensionlm_runtime_loaded == false

## Non-claims

This is not a broad natural-language understanding claim, not an external benchmark victory claim, not live TensionLM runtime integration, and not general theorem proving.

The proposer remains candidate data.

The typed verifier remains proof authority.
