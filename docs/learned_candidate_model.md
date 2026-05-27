# Learned Candidate Model

`TS-Reasoner v2.0.0: Learned Candidate Model` adds a tiny learned
candidate/channel model before the typed verifier.

The boundary is unchanged:

```text
learned model proposes and ranks
-> candidate claims enter the bridge
-> TS-Reasoner typed channels verify
-> accepted / rejected / abstained candidates are written to a receipt
```

The learned model is not proof authority. Candidate confidence is metadata.
Accepted candidates still require typed-channel support, and candidate edges do
not enter the proof-support graph.

## Scope

This release trains a dependency-light pure-Python linear model on controlled
structured reasoning examples. It does not train a full language model and does
not load TensionLM.

Inputs:

- premises,
- query text,
- candidate claims,
- candidate confidence metadata,
- graph-derived features.

Outputs:

- candidate ranking score,
- candidate status prediction,
- resolver prediction,
- channel activation prediction.

The predictions are advisory. The candidate bridge reruns TS-Reasoner typed
verification before any candidate is accepted.

## Commands

```bash
python3 scripts/build_learned_candidate_dataset.py
python3 scripts/train_learned_candidate_model.py
python3 scripts/evaluate_learned_candidate_model.py
python3 scripts/demo_learned_candidate_model.py
```

Generated artifacts:

- `data/learned_candidate_model_train.jsonl`
- `data/learned_candidate_model_eval.jsonl`
- `data/learned_candidate_model_stress.jsonl`
- `artifacts/learned_candidate_model.json`
- `artifacts/learned_candidate_model_report.json`
- `artifacts/learned_candidate_model_stress_report.json`
- `artifacts/learned_candidate_model_receipt.json`
- `artifacts/learned_candidate_model_demo.json`

## Demo

Input:

```text
Premises:
All A are B.
All B are C.
All C are D.

Question:
Are all A D?
```

Model candidates:

```text
All A are D
All D are A
A equals D
```

Verifier output:

- accepted: `All A are D`
- rejected: `All D are A` through `directionality`
- rejected: `A equals D` through `identity_preservation`

The demo trace records `candidate_graph_contamination_count: 0`.

## Metrics

The evaluator records:

- `candidate_ranking_accuracy`
- `accepted_candidate_support_rate`
- `bad_candidate_rejection_rate`
- `verifier_beats_model_confidence_rate`
- `channel_activation_accuracy`
- `resolver_prediction_accuracy`
- `abstention_accuracy`
- `candidate_graph_contamination_count`
- `trace_schema_validity`
- `deeper_chain_success_rate`
- `distractor_robustness`

The most important receipt field remains
`candidate_graph_contamination_count: 0`. It proves the learned candidate layer
does not insert model outputs into proof support.

## Non-Claims

This release does not claim:

- chatbot behavior,
- instruction following,
- general theorem proving,
- broad natural-language understanding,
- live TensionLM integration,
- that model confidence is proof.

It claims only that a small learned candidate model can propose and rank
structured candidate claims while typed verifier channels preserve authority and
failure reasons.
