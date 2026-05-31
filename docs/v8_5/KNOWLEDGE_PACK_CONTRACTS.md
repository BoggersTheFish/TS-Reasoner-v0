# TS-Reasoner v8.5.0: Knowledge Pack Contracts

v8.5.0 adds bounded knowledge-pack import contracts.

The purpose is to make portable TS state safe to import without promoting unsupported claims into proof.

## What v8.5.0 adds

- schema version checks
- old-schema migration
- invalid-pack quarantine
- accepted-claim import
- branch-world preservation
- repair-target preservation
- provenance-record preservation
- unsupported-claim quarantine
- zero candidate graph contamination gate

## Killer case

A knowledge pack contains:

- accepted claims
- branch worlds
- repair targets
- provenance records
- one unsupported hostile claim

Expected result:

- valid accepted state imports
- branch worlds are preserved
- repair targets are preserved
- provenance records are preserved
- unsupported hostile claim is quarantined
- unsupported claim is not promoted
- candidate graph contamination remains zero

## Boundary

Knowledge-pack import is not proof.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
