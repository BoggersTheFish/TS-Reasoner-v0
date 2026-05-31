# TS-Reasoner v9.0.0: Verifier-First Runtime Kernel

v9.0.0 packages the v8 immune-system ladder into one bounded runtime kernel.

The kernel processes events and routes them into safe actions:

- quarantine
- open repair
- branch world
- quarantine pack
- audit snapshot
- receipt record

## Kernel contract

Input:

`kernel.process_event(event, state)`

Output:

- policy action
- updated bounded state
- audit snapshot
- receipt
- zero candidate graph contamination gate

## What v9.0.0 proves

The system can route hostile claims, unsupported claims, trusted revisions, and unsafe knowledge-pack events through one verifier-first runtime surface.

Candidate data does not mutate accepted common ground.

## Boundary

The runtime kernel is not broad natural-language understanding.

It is not a general theorem prover.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
