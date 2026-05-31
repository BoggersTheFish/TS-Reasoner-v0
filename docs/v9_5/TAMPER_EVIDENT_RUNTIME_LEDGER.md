# TS-Reasoner v9.5.0: Tamper-Evident Runtime Ledger

v9.5.0 makes the runtime state ledger tamper-evident.

Each ledger entry is hash-chained:

- previous hash
- entry payload
- entry hash

If an entry is edited, deleted, or reordered, verification fails.

## What v9.5.0 adds

- deterministic canonical JSON hashing
- SHA-256 ledger entry hashes
- previous-hash chaining
- chain verification
- tamper detection test
- empty-session safety
- zero candidate graph contamination gate

## Boundary

The hash chain proves ledger integrity, not claim truth.

Ledger entries are audit records, not proof.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
