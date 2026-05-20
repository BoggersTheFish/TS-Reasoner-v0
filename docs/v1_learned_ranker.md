# v1 Learned Ranker Branch

The `v1-learned-ranker` branch keeps the v0 trace contract and adds the first learned tension-field experiment.

```text
v0 = hand-coded tension field
v1 = learned tension field
v2 = learned candidate generator
v3 = generator + ranker + verifier loop
```

## Goal

Replace or augment `HeuristicTensionRanker` with `LearnedTensionRanker` while preserving the public output schema:

```text
ReasonerOutput
  question
  premises
  candidates
  selected_chain
  tension_score
  cig_check
  repairs
  final_answer
  trace
```

The learned ranker still returns `TensionScore`, so downstream trace export, repair suggestions, and pipeline selection keep the same shape.

## Synthetic Data

Synthetic rows are generated from the existing example patterns plus symbol/name variants:

- valid all/all syllogism
- invalid some/all quantifier jump
- direct contradiction
- missing premise

Each candidate chain becomes one row with:

- task ID
- task type
- candidate chain ID
- question
- premises
- extracted numeric features
- heuristic global tension
- synthetic answer-quality label
- issue kinds

The label is a ranking target:

```text
label = 0 -> candidate should rank as the stable answer path
label = 1 -> candidate should rank lower
```

These labels are synthetic release scaffolding, not benchmark ground truth.

## Scripts

```bash
python3 scripts/build_synthetic_dataset.py
python3 scripts/train_learned_ranker.py
python3 scripts/compare_rankers.py
python3 -m unittest discover
```

Generated artifacts:

- `data/synthetic_ranker_dataset.jsonl`
- `data/synthetic_ranker_dataset_summary.json`
- `artifacts/learned_ranker_v1.json`
- `artifacts/learned_ranker_training_summary.json`
- `artifacts/ranker_comparison.json`

## Current Comparison

The generated comparison currently reports:

```text
learned_label_accuracy: 1.0
heuristic_label_accuracy: 0.7778
selection_agreement: 1.0
selection_tasks: 32
output_schema_identical: true
```

Interpretation:

- The learned ranker matches the synthetic answer-quality labels on the held-out split.
- The heuristic ranker is still the v0 reference field, but its raw threshold is not identical to the answer-quality target.
- The learned ranker and heuristic pipeline select the same candidate on the synthetic task set.
- This is a tiny branch experiment, not a general proof-ranking benchmark.

