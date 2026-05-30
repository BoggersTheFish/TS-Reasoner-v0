# TS-Chat v0.5 — Candidate Language Rules

TS-Chat v0.5 adds an inspectable candidate-language layer.

Instead of composing exactly one hardcoded response, TS-Chat now generates response candidates from explicit language rules, scores them using common-ground/verifier signals, and selects the best candidate.

## Claim

Language can be candidate-called.

The chat system can generate multiple possible phrasings from graph state, score them, and record which rule produced the final response.

## Adds

- `ts_reasoner.candidate_language`
- response candidate dataclass
- language rule IDs
- candidate scores and selection reasons
- candidate selection receipts
- v0.5 deterministic demo receipt

## Boundary

This is not an LLM.

It is a scratch TS-native candidate language runtime:
- bounded rules
- explicit candidates
- inspectable selection
- no external model
