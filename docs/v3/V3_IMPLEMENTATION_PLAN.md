# TS-Reasoner v3.0 Implementation Plan

v3.0 should be implemented as a bounded, inspectable flagship model release.

## Phase 1 — Dataset

Build a unified v3 dataset from:

- v2.7 verifier trace rows
- v2.9 active-learning challenge rows
- v2.9 augmented training rows
- benchmark split metadata

Output:

```text
artifacts/v3/v3_training_dataset.jsonl
artifacts/v3/v3_dataset_summary.json
```

Dataset row schema should include:

- case_id
- split
- tags
- input_claim
- candidate features
- model prediction features
- verifier status
- verifier channels
- failure reason
- target status
- target channel flags
- boundary metadata

## Phase 2 — Model

Train `VerifierGuidedCandidateModel`.

Initial implementation should stay small and inspectable:

- linear / logistic-style status head
- channel prediction heads
- proposal quality head
- deterministic JSON serialization

Output:

```text
artifacts/v3/verifier_guided_candidate_model.json
```

## Phase 3 — Evaluation

Evaluate against:

- majority baseline
- confidence baseline
- v2.8 training-loop smoke model
- v2.9 active-learning model

Output:

```text
artifacts/v3/verifier_guided_candidate_model_report.json
artifacts/v3/v3_eval_predictions.jsonl
```

## Phase 4 — Boundary audit

Check:

- accepted_without_typed_support_count
- candidate_graph_contamination_count
- verifier/model separation
- boundary metadata presence
- trace schema validity

## Phase 5 — Demo

Add a small demo command:

```bash
python3 scripts/v3/run_v3_demo.py
```

Demo should show:

- input prompt
- candidate claims
- model status prediction
- typed verifier final decision
- failure channels when rejected/abstained
- proof-boundary note

## Phase 6 — Release docs

Create:

```text
docs/v3/V3_MODEL_CARD.md
docs/v3/V3_EVAL_REPORT.md
docs/v3/V3_LIMITATIONS.md
```

## Phase 7 — Release decision

Only tag v3.0.0 if gates pass. Otherwise convert the work into v2.10 and keep v3.0 reserved for the real flagship.
