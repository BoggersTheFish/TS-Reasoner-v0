# TS-Reasoner v11.9.0: Neural TS-Proposer Tiny

v11.9.0 adds a tiny pure-stdlib neural proposer baseline.

It uses:

- hashed sparse verifier-trace features
- a tiny tanh hidden layer
- softmax classifiers
- SGD training
- verifier-gated proposed `yes` answers

It predicts:

- answer
- status
- support channel or reason

## Boundary

This is not a broad neural language model and not a GPT-2 replacement.

It is a tiny neural proposer over verifier-labelled traces. Proposed labels are candidate outputs only. The typed verifier remains proof authority. Generated text and model confidence remain non-proof.
