# TS-Reasoner v8.6.0: Reasoning Diff/Patch Language

v8.6.0 adds a bounded reasoning diff/patch language.

The purpose is to make TS state changes auditable.

Every important state transition can become a typed patch:

- `claim_added`
- `claim_quarantined`
- `repair_opened`
- `repair_resolved`
- `world_branched`
- `pack_imported`

## What this proves

The system can describe state changes without confusing audit records for proof.

A patch records what changed, why it changed, and whether verifier support is required.

## Boundary

Patches are audit records, not proof.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
