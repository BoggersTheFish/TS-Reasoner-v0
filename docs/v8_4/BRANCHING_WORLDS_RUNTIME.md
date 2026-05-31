# TS-Reasoner v8.4.0: Branching Worlds Runtime

v8.4.0 adds a bounded branching-worlds runtime.

The purpose is to let trusted revisions or missing-support repair candidates live in isolated worlds without contaminating accepted common ground.

## What v8.4.0 adds

- `world_id`
- `parent_world_id`
- `branch_reason`
- branch worlds for trusted contradictions
- branch worlds for missing-support repair candidates
- quarantine behavior for identity violations
- no automatic merge
- zero candidate graph contamination gate

## Killer case

Base world:

all birds fly

Trusted revision:

some birds do not fly

Expected result:

- base world keeps `all birds fly`
- branch world contains `some birds do not fly`
- branch links to parent world
- no automatic merge occurs
- candidate graph contamination remains zero

## Boundary

Branching is not acceptance.

Generated text is not proof.

Candidate generation is not proof.

Model confidence is not proof.

Typed verifier support remains the proof boundary.
