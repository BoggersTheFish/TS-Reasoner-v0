# TS-Reasoner v9.4.0: Runtime State Ledger

v9.4.0 adds a bounded append-only runtime state ledger.

The ledger records each runtime event result as an audit entry:

- event index
- case ID
- action
- original event
- kernel receipt
- audit snapshot
- contamination count

## What v9.4.0 adds

- append-only ledger entries
- per-event receipt preservation
- per-event audit preservation
- ordered ledger indexing
- empty-session safety
- zero candidate graph contamination gate

## Boundary

The ledger is an audit trail, not proof.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
