# TS-Reasoner v11.5.0: Adversarial Claim Fuzzer

v11.5.0 attacks brittleness in the verifier-first arena.

It mutates generated curriculum tasks with:

- reversed premise order
- duplicate premises
- irrelevant premise injection
- confidence bait
- contradiction injection
- malformed claim injection
- noisy surface wrappers
- paragraph noise wrappers

The goal is not broad open-domain adversarial robustness. The goal is narrower and receipt-backed:

- wrong accepts remain zero
- accepted without typed support remains zero
- candidate graph contamination remains zero
- parser crashes remain zero
- contradiction rejection remains correct
- unsupported-claim abstention remains correct

## Boundary

This is deterministic adversarial fuzzing over bounded verifier-first tasks.

Generated text remains candidate data. Confidence remains non-proof. The verifier remains proof authority.
