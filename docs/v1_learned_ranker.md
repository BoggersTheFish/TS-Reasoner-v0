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

Synthetic rows are generated from the existing example patterns plus train/heldout template families:

- valid all/all syllogism
- invalid some/all quantifier jump
- direct contradiction
- missing premise

Training uses symbolic forms such as `A/B/C`, `D/E/F`, and `G/H/I`.

Heldout evaluation uses natural terms such as:

- `pilots/engineers/careful`
- `mammals/animals/living`
- `tools/objects/useful`

Adversarial candidates are added for invalid tasks. These candidates use confident surface wording such as `Obviously`, `Certainly`, or `Definitely` while the underlying logic is wrong.

Each candidate chain becomes one row with:

- task ID
- task type
- train/eval split
- template family
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
- `artifacts/learned_ranker_v1_no_cig.json`
- `artifacts/learned_ranker_v1_no_issue_kinds.json`
- `artifacts/learned_ranker_training_summary.json`
- `artifacts/ranker_comparison.json`

## Current Comparison

The generated comparison currently reports:

```text
train_template_family: symbolic
heldout_template_family: heldout_natural
heldout_rows: 96
heldout_tasks: 32
adversarial_heldout_rows: 24
output_schema_identical: true
```

Current ablation table:

```text
ranker                                      row_acc  select_acc  adv_avoid
heuristic_ranker                            0.5833   1.0000      1.0000
learned_ranker                              1.0000   1.0000      1.0000
learned_ranker_without_cig_features         1.0000   1.0000      1.0000
learned_ranker_without_issue_kind_features  1.0000   1.0000      1.0000
random_baseline                             0.5312   0.5312      0.5417
```

Interpretation:

- The learned ranker matches the synthetic answer-quality labels on heldout natural templates.
- The heuristic ranker is still the v0 reference field and selects stable candidates, but its raw tension threshold is not identical to the answer-quality label.
- In this small split, CIG-derived features and issue-kind features are redundant enough that each single ablation still solves the heldout set.
- The random baseline shows the task is not solved by arbitrary candidate ordering.
- This is a tiny branch experiment, not a general proof-ranking benchmark.

## Caveat

Because all learned ablations reach 1.0 on the current heldout set, this eval should be treated as a schema-preserving learned-ranker smoke test, not evidence that the learned model has robust general reasoning ability. The next eval should add harder cases where CIG provenance and issue-kind features are necessary.
