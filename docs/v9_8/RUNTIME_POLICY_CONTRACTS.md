# TS-Reasoner v9.8.0: Runtime Policy Contracts

v9.8.0 adds explicit runtime policy contracts.

Runtime actions are no longer only action strings. They are checked against a
machine-readable contract document that defines required state keys, required
receipt keys, and the proof-boundary rule for each action.

## What v9.8.0 adds

- policy contract schema
- contract definitions for quarantine, repair, branch, pack check, checkpoint, and restore actions
- runtime action contract evaluator
- invalid or missing contract field rejection path
- zero candidate graph contamination gate

## Boundary

Policy contracts define runtime behavior.

They do not prove claim truth.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
