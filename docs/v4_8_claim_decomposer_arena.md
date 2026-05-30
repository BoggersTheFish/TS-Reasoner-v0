# TS-Reasoner v4.8 — Claim Decomposer Arena

v4.8 extends the verifier-first answer arena with bounded claim decomposition.

Generated answers can now be messy explanations. TS-Reasoner extracts bounded `all X are Y` relation claims before deciding whether the candidate should be accepted, rejected, or abstained.

## Claim

Messy generated answers are decomposed into bounded relation claims before TS-Reasoner selects, rejects, or abstains using typed verifier support.

## What this release adds

- `ts_reasoner.claim_decomposer`
- `ts_reasoner.decomposed_answer_arena`
- `data/v4_8/claim_decomposer_arena_cases.jsonl`
- `scripts/v4_8/evaluate_claim_decomposer_arena.py`
- `artifacts/v4_8_claim_decomposer_arena_report.json`

## Boundary

This is still bounded.

It does not claim broad NLP, general theorem proving, external benchmark victory, or live TensionLM runtime integration.

The important rule remains:

- generated text is not proof
- confidence is not proof
- candidate source is not proof
- extracted candidate claims do not contaminate the proof graph
- typed verifier support remains proof authority

## Expected headline

- case count: 8
- candidate count: 24
- arena selection accuracy: 1.0
- wrong accepts: 0
- accepted without typed support: 0
- candidate graph contamination: 0
- all gates passed: true
