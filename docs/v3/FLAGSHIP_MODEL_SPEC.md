# TS-Reasoner v3.0 Flagship Model Spec

Working title:

```text
TS-Reasoner v3.0 — Verifier-Guided Candidate Model
```

## 1. Purpose

v3.0 is the first flagship model release in TS-Reasoner.

The goal is not to claim broad language-model capability. The goal is to release a bounded reasoning model that learns from typed verifier traces and active-learning challenge rows while preserving a hard proof boundary.

Core claim:

```text
A bounded candidate-status model can learn from verifier traces and active-learning rows, improve over simple baselines on heldout reasoning candidates, and remain subordinate to typed verifier channels for proof authority.
```

## 2. Architecture

The v3.0 architecture is:

```text
natural-language input
→ bounded claim parser
→ candidate claim generator/ranker
→ verifier-guided candidate model
→ typed verifier channels
→ accept / reject / abstain
→ verifier trace rows
→ active-learning challenge rows
→ retraining loop
```

## 3. Boundary

v3.0 must preserve this boundary:

- The model proposes, ranks, and predicts candidate status.
- Typed verifier channels decide proof status.
- Model confidence is never proof authority.
- Accepted claims require typed support.
- Rejected/abstained claims must preserve failure reason and channel evidence.
- No TensionLM runtime is required for v3.0.
- No broad NLP or chatbot claim is made.
- The v3.0 model is a bounded reasoning-status model, not a general LLM.

## 4. Inputs

v3.0 training inputs should include:

- `data/verifier_trace_training_data_v27.jsonl`
- `data/active_learning_challenge_v29.jsonl`
- `data/active_learning_augmented_training_v29.jsonl`
- v2.5 benchmark harness cases
- v2.6 candidate model outputs
- v2.7 verifier trace rows
- v2.8 training-loop smoke rows
- v2.9 active-learning challenge rows

## 5. Model

The v3.0 model should be a small, inspectable model trained on verifier-derived targets.

Minimum acceptable model:

```text
VerifierGuidedCandidateModel
```

It should predict:

- candidate ranking score
- target status: accepted / rejected / abstained
- target channel set
- proposal quality
- error flags:
  - reverse error
  - identity error
  - quantifier error
  - contradiction error
  - malformed error
  - unsupported claim

## 6. Required artifacts

v3.0 should produce:

```text
artifacts/v3/verifier_guided_candidate_model.json
artifacts/v3/verifier_guided_candidate_model_report.json
artifacts/v3/verifier_guided_candidate_model_receipt.json
artifacts/v3/v3_training_dataset.jsonl
artifacts/v3/v3_eval_predictions.jsonl
```

Docs:

```text
docs/v3/FLAGSHIP_MODEL_SPEC.md
docs/v3/V3_MODEL_CARD.md
docs/v3/V3_EVAL_REPORT.md
docs/v3/V3_LIMITATIONS.md
```

Scripts:

```text
scripts/v3/build_v3_training_dataset.py
scripts/v3/train_v3_verifier_guided_model.py
scripts/v3/evaluate_v3_verifier_guided_model.py
scripts/v3/run_v3_demo.py
```

Tests:

```text
tests/test_v3_training_dataset.py
tests/test_v3_verifier_guided_model.py
tests/test_v3_release_gates.py
```

## 7. Evaluation gates

v3.0 should not release unless all gates pass.

Minimum gates:

- status accuracy on heldout eval >= 0.90
- beats majority baseline by >= 0.20
- beats confidence baseline by >= 0.20
- accepted-without-typed-support count = 0
- candidate graph contamination count = 0
- trace schema validity = 1.0
- boundary metadata present in model/report/receipt
- active-learning challenge accuracy >= v2.9 active-learning baseline
- all tests pass

## 8. Investor-readable claim

If gates pass, public claim:

```text
TS-Reasoner v3.0 is a bounded verifier-guided reasoning model. It learns from typed verifier traces and active-learning challenge rows to predict candidate reasoning status while preserving typed verifier channels as proof authority.
```

Do not claim:

- broad AGI
- general theorem proving
- general natural-language understanding
- replacement for LLMs
- TensionLM runtime integration
- truth without verifier authority

## 9. v3.0 release decision

v3.0 should be released only if it is clearly stronger than v2.9 in one of these ways:

1. better unified model over all previous data;
2. cleaner model/report/receipt story;
3. stronger heldout challenge performance;
4. clearer demo path for investors;
5. better proof-boundary evidence.

If it cannot beat v2.9 honestly, release v3.0 should be delayed and the next release should be v2.10 instead.
