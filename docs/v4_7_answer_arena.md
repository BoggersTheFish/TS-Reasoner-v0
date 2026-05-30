# TS-Reasoner v4.7 — Verifier-First Answer Arena

v4.7 introduces a bounded multi-proposer answer arena.

Candidate generators propose answers. TS-Reasoner evaluates those answers as candidate data and selects, rejects, or abstains using typed verifier support rather than confidence, fluency, or source identity.

## Claim

Competing generated answers enter as candidate data; TS-Reasoner selects, rejects, or abstains using typed verifier support rather than confidence.

## What this release adds

- `ts_reasoner.answer_arena`
- `data/v4_7/answer_arena_cases.jsonl`
- `scripts/v4_7/evaluate_answer_arena.py`
- `artifacts/v4_7_answer_arena_report.json`

## Bounded scope

The arena currently supports simple `all X are Y` relation claims and transitive support over premise edges.

It is not a broad NLP claim, theorem-proving claim, or external benchmark victory claim.

## Boundary

- generated text is not proof
- confidence is not proof
- candidate source is not proof
- typed verifier support remains proof authority
- candidate claims do not contaminate the proof graph

## Headline metrics

Expected v4.7 receipt:

- arena selection accuracy: 1.0
- confidence top accuracy: below verifier accuracy
- wrong accepts: 0
- accepted without typed support: 0
- candidate graph contamination: 0
- all gates passed: true
