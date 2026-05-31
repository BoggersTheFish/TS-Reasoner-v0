# TS-Reasoner v9.9.0: Runtime Recovery Drill

v9.9.0 adds a recovery drill across replay, tamper-evident ledger,
checkpoint, restore, and continued runtime processing.

The drill verifies that a checkpoint can be restored, corrupt checkpoints are
rejected, reordered ledgers are rejected, missing-event replay diverges from
the complete session, and restored state can continue processing new events.

## What v9.9.0 adds

- corrupt checkpoint rejection
- reordered ledger rejection
- missing-event replay divergence check
- restore-then-continue runtime path
- recovery drill receipt
- zero candidate graph contamination gate

## Boundary

Recovery proves runtime state integrity and continuity.

It does not prove claim truth.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
