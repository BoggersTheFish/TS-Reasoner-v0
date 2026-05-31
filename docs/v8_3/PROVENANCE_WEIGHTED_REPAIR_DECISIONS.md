# TS-Reasoner v8.3.0: Provenance-Weighted Repair Decisions

v8.3.0 adds bounded provenance-weighted repair decisions.

The purpose is to stop repair policy from treating all sources equally.

A candidate claim from a hostile or copied source should not outweigh a canonical authority claim just because it appears multiple times.

## What v8.3.0 adds

- source trust weights
- dependency cluster penalties
- authority source bonuses
- correlated-source downweighting
- winning-claim selection
- repair action selection
- zero candidate graph contamination gate

## Killer case

Canonical authority says:

no external llm was used

Two correlated hostile candidates say:

external llm was used

Expected result:

- canonical claim wins
- hostile correlated claims are downweighted
- incoming contradiction is rejected and quarantined
- accepted claim is preserved
- candidate graph contamination remains zero

## Boundary

Provenance pressure is not proof.

Generated text is not proof.

Candidate generation is not proof.

Model confidence is not proof.

Typed verifier support remains the proof boundary.
