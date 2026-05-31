# TS-Reasoner v10.1: Epistemic Microkernel

v10.1 adds an immutable verifier microkernel wrapper for accepted common ground.
Userspace proposals are represented as requests. Accepted state mutates only
through kernel gates, and each transition emits a canonical JSON SHA-256
receipt.

Boundary:

- Generated text is not proof.
- Model confidence is not proof.
- Runtime integrity is not claim truth.
- Accepted common ground mutates only through kernel verifier gates.
