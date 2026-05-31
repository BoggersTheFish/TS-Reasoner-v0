# TS-Reasoner v8.1.0: Contradiction Repair Policy Engine

v8.1.0 adds a bounded contradiction repair policy engine.

The purpose is to stop contradictions from being handled as vague rejection events.

The policy engine turns a contradiction into a typed action:

- reject and quarantine
- reject and open repair
- branch worlds
- reject and explain
- open missing bridge repair
- accept as reinforcement
- abstain and request support

## Core rule

Contradictory candidate data must not contaminate accepted common ground.

## Killer case

Accepted invariant:

no external llm was used

Hostile incoming candidate:

external llm was used

Expected policy:

reject_and_quarantine

The accepted invariant is preserved. The hostile candidate is not accepted. A repair target is created. Candidate graph contamination remains zero.

## Boundaries

v8.1.0 is not a broad natural-language understanding system.

It is not a general theorem prover.

It does not make candidate generation, model confidence, or generated text into proof.

Typed verifier support remains the proof boundary.
