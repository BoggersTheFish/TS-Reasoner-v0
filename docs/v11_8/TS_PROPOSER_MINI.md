# TS-Reasoner v11.8.0: TS-Proposer-Mini Baseline

v11.8.0 adds the first trained proposer baseline.

TS-Proposer-Mini is a tiny stdlib hashed-perceptron model trained on the v11.7 verifier trace dataset.

It predicts:

- answer: `yes`, `no`, or `abstain`
- status: `accepted`, `rejected`, or `abstained`
- support channel or reason

The proposer is not proof authority. Its predictions are routed through a verifier gate. A proposed `yes` only survives as `yes` when the typed verifier accepts the candidate claim with support.

## Boundary

This is not a neural language model and not a broad GPT-2 replacement.

It is the first trained proposer baseline over verifier-labelled traces. The verifier remains proof authority. Generated/proposed text and model confidence remain non-proof.
