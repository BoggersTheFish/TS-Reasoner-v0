# Learned Candidate Model Adversarial Stress

TS-Reasoner v2.1 adds an adversarial stress layer for the learned candidate model introduced in v2.0.

The goal is not to make the learned model proof-authoritative. The learned model remains a proposal/ranking layer. Typed verifier channels remain the only authority for accepting, rejecting, or abstaining on candidate claims.

## Stress cases

The adversarial dataset includes:

- high-confidence false candidates
- reverse inference traps
- some/all quantifier escalation traps
- malformed candidates with fake confidence
- unsupported but plausible candidates
- distractor-heavy premise sets
- contradiction traps
- identity-collapse traps
- missing-provenance candidates

## Boundary claim

A candidate can be high-confidence and still fail. Confidence is metadata only. A candidate is accepted only when typed verifier support exists.

## Command

Run:

    python3 scripts/evaluate_learned_candidate_model_adversarial.py
    python3 -m unittest discover -q

## Public claim level

Experimental. This is structured adversarial evidence for verifier-boundary behavior, not a broad claim of general reasoning capability.
