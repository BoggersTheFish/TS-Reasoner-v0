# TS-Reasoner v3.0 Investor Narrative

## One-line framing

```text
TS-Reasoner v3.0 is a bounded verifier-guided reasoning model that learns from its own typed verification traces while keeping proof authority separate from model confidence.
```

## The problem

Modern language models can produce confident reasoning-shaped text without a hard proof boundary.

The core failure mode is not just hallucination. It is authority confusion:

- a model proposes an answer;
- confidence makes the answer feel true;
- the system lacks an inspectable typed verifier boundary;
- errors can be fluent, hidden, or hard to audit.

TS-Reasoner attacks that problem at a small, inspectable scale.

## The v3.0 idea

v3.0 separates three roles:

1. candidate generation and ranking;
2. typed verifier decision-making;
3. verifier-derived training feedback.

The model can learn from verifier traces, but the verifier remains the authority.

```text
model prediction ≠ proof
typed verifier support = proof boundary
```

## What has already been proven before v3.0

- v2.4: bounded natural-language claim ingestion;
- v2.5: reusable benchmark harness;
- v2.6: Candidate Model v2 beats confidence ordering while preserving verifier authority;
- v2.7: verifier traces export into supervised training rows;
- v2.8: verifier trace rows train a tiny status model above baselines;
- v2.9: verifier-labeled challenge rows improve the model in an active-learning loop.

## Why v3.0 matters

v3.0 is the first unified model release that turns the previous ladder into one coherent artifact:

```text
bounded parser
→ candidate model
→ typed verifier
→ verifier trace dataset
→ active-learning loop
→ verifier-guided model
```

This is not a claim of general intelligence. It is a claim of controlled reasoning-model development with a hard audit boundary.

## Investor-readable claim shape

```text
We are building reasoning models that learn from verification without being allowed to replace verification.
```

That matters because the safety and interpretability story is built into the training loop rather than bolted on afterwards.

## What v3.0 must demonstrate

- a named model artifact;
- a reproducible training dataset;
- heldout evaluation;
- comparison to majority/confidence/v2.8/v2.9 baselines;
- no accepted claim without typed support;
- no candidate graph contamination;
- explicit limitations;
- a local demo that a non-specialist can run.

## What v3.0 must not claim

- AGI;
- broad natural-language understanding;
- general theorem proving;
- replacement for LLMs;
- truth from model confidence;
- TensionLM runtime integration unless separately implemented and evaluated.

## Funding narrative

The fundable thesis is:

```text
Instead of training models to sound more certain, train bounded models to learn from typed verification traces while keeping verification authoritative.
```

This positions TS-Reasoner as an interpretability-first reasoning substrate:

- inspectable failure reasons;
- typed verifier channels;
- training data derived from verifier decisions;
- active learning driven by model failure;
- hard separation between prediction and proof.

## v3.0 release line

If the release gates pass, v3.0 can be described as:

```text
TS-Reasoner v3.0 is a bounded verifier-guided candidate model trained from typed verifier traces and active-learning rows, evaluated with proof-boundary gates that prevent model confidence from becoming proof authority.
```
