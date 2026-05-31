# TS-Reasoner v9.6.0: Runtime Checkpoint / Restore

v9.6.0 adds bounded runtime checkpoint and restore.

A checkpoint contains:

- schema
- case ID
- final runtime state
- action trace
- hash-chained ledger
- ledger head hash
- contamination count

## What v9.6.0 adds

- checkpoint creation
- checkpoint restore
- head-hash verification
- ledger hash-chain verification before restore
- empty-session restore safety
- zero candidate graph contamination gate

## Boundary

Checkpoint restore proves runtime state integrity, not claim truth.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
