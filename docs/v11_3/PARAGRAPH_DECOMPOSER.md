# TS-Reasoner v11.3.0: Paragraph Claim Decomposer

v11.3.0 adds a bounded paragraph intake layer.

It can decompose short natural-language reasoning paragraphs into:

- canonical verifier premises
- one target claim/question
- ignored unparseable sentences
- a safe abstention state when no parseable question exists

Example:

```text
Generated text counts as candidate data.
Candidate data is a type of untrusted material.
Is generated text untrusted material?

Decomposes to:

{
  "premises": [
    "all generated text are candidate data",
    "all candidate data are untrusted material"
  ],
  "candidate_claim": "all generated text are untrusted material"
}

The typed verifier then decides whether the candidate claim is accepted, rejected, or abstained.

Boundary

This is bounded paragraph decomposition, not broad natural-language understanding.

Generated text remains candidate data. The verifier remains proof authority. Unsupported, reversed, ambiguous, or malformed inputs must not enter accepted common ground.
