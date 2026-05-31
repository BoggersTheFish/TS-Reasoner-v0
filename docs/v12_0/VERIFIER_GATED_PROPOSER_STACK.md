# TS-Reasoner v12.0.0: Verifier-Gated Proposer Stack

v12.0.0 packages the v11 line into one end-to-end stack:

```text
paragraph input
→ bounded paragraph decomposition
→ trained proposer prediction
→ typed verifier gate
→ final yes/no/abstain answer
→ trace/receipt

The trained proposer predicts candidate answer/status/channel labels. The typed verifier remains final authority.

A proposed yes is not accepted because the proposer said yes. It is accepted only when the typed verifier accepts the decomposed claim with support.

Boundary

This is not a broad neural language model, not a general theorem prover, and not a GPT-2 replacement.

This release proves the bounded verifier-gated proposer stack runs end-to-end with traceable outputs and zero wrong accepts inside the controlled arena. Proposed labels, generated text, and model confidence remain non-proof.
