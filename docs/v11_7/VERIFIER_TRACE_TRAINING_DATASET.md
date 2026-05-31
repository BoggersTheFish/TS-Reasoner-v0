# TS-Reasoner v11.7.0: Verifier Trace Training Dataset

v11.7.0 creates verifier-labelled JSONL training data for future proposer models.

Each row contains:

- natural/bounded input prompt
- canonical premises
- candidate claim
- target answer: `yes`, `no`, or `abstain`
- target status: `accepted`, `rejected`, or `abstained`
- support channel or rejection/abstention reason
- support premises
- typed verifier trace hash when accepted

The dataset is built from:

- procedural curriculum tasks
- adversarial fuzzer tasks
- paragraph decomposition tasks

## Boundary

This is not a trained model yet.

This release creates supervised data for a future proposer. Labels come from typed verifier replay, not model confidence, not generated text, and not human vibes. The verifier remains proof authority.
