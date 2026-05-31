# TS-Reasoner v11.0.0: GPT-2 Boundary Arena

v11.0 demonstrates a reproducible verifier-first boundary where TS-Reasoner
beats GPT-2-small on controlled reasoning, contradiction rejection,
support-path recovery, and unsupported-claim abstention.

Boundary:

- This is not a broad chatbot victory.
- This is not a full language-model replacement claim.
- This is a verifier-first reasoning boundary result.
- GPT-2 generates; TS verifies.

The arena runs the same 100 frozen tasks through:

1. GPT-2-small baseline prompt, parse, and score.
2. TS-Reasoner premise graph support-path derivation or rejection/abstention.
3. Head-to-head comparison with receipt-backed gates.

Required TS gates:

- support-path accuracy: `1.0`
- contradiction rejection rate: `1.0`
- unsupported abstention rate: `1.0`
- wrong accept count: `0`
- accepted without typed support: `0`
- candidate graph contamination: `0`

Run:

```bash
python3 scripts/v11_0/evaluate_gpt2_boundary_arena.py
python3 -m unittest discover -q
```

## Current Release Authority

Current release: v11.7.0, Verifier Trace Training Dataset

This document is the required internal release-authority surface for v11.7.0.
The current release title is Verifier Trace Training Dataset.

Boundary:
- Generated text is not proof.
- Model confidence is not proof.
- Candidate generation is not proof.
- Typed verifier support remains the proof boundary.
