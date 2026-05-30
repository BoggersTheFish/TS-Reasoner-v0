# TS-Reasoner v4.9 — Unsupported Claim Audit

v4.9 tightens the verifier-first answer arena.

v4.8 could decompose messy generated answers into bounded relation claims. v4.9 adds explanation auditing: a candidate cannot be accepted if its explanation contains unsupported bounded claims, even when the final answer claim is supported.

## Claim

Generated answers are rejected when their explanations contain unsupported bounded claims, even if the final answer claim is typed-supported.

## What this release adds

- `ts_reasoner.claim_audit`
- `data/v4_9/unsupported_claim_audit_cases.jsonl`
- `scripts/v4_9/evaluate_unsupported_claim_audit.py`
- `artifacts/v4_9_unsupported_claim_audit_report.json`

## Boundary

- generated text is not proof
- confidence is not proof
- candidate source is not proof
- extracted candidate claims do not contaminate the graph
- typed verifier support remains proof authority

## Scope

This is bounded all-X-are-Y relation auditing.

It is not broad NLP, general theorem proving, an external benchmark victory claim, or live TensionLM runtime integration.

## Expected headline

- case count: 8
- candidate count: 24
- unsupported-claim stress candidates: greater than 0
- arena selection accuracy: 1.0
- wrong accepts: 0
- accepted without typed support: 0
- accepted with unsupported claims: 0
- candidate graph contamination: 0
- all gates passed: true
