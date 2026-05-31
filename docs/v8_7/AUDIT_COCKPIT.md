# TS-Reasoner v8.7.0: Audit Cockpit

v8.7.0 adds a bounded audit cockpit.

The purpose is to inspect TS-Reasoner state without mutating accepted common ground.

Supported audit views:

- `status`
- `repairs`
- `worlds`
- `quarantine`
- `patches`
- `audit`

## What v8.7.0 adds

- accepted claim counts
- repair target summaries
- branch world summaries
- quarantine summaries
- reasoning patch summaries
- full audit summaries
- zero candidate graph contamination gate

## Boundary

Audit reports do not mutate state.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
