# TS-Reasoner v3.0 Model Card

## Model

```text
VerifierGuidedCandidateModel
```

## Summary

TS-Reasoner v3.0 is a bounded verifier-guided candidate model.

It predicts candidate reasoning status and likely verifier channels from verifier-derived training data. It does not decide proof. Typed verifier channels remain proof authority.

## Public claim

```text
A bounded verifier-guided candidate model can learn from typed verifier traces and active-learning rows, beat simple baselines on heldout candidate-status evaluation, and preserve a hard proof boundary where model confidence never becomes proof authority.
```

## Inputs

- v3 unified training dataset
- verifier trace rows
- active-learning challenge rows
- candidate features
- verifier target status/channel labels

## Outputs

- predicted status: accepted / rejected / abstained
- predicted verifier channels
- predicted proposal quality
- boundary metadata

## Evaluation

Current v3 gate metrics:

```text
status_accuracy: 1.0
channel_prediction_accuracy: 0.9888
majority_baseline_accuracy: 0.4286
confidence_baseline_accuracy: 0.5714
beats_majority_margin: 0.5714
beats_confidence_margin: 0.4286
accepted_without_typed_support_count: 0
candidate_graph_contamination_count: 0
trace_schema_validity: 1.0
all_gates_passed: true
```

## Boundary

- The model is not proof authority.
- Typed verifier channels remain proof authority.
- Model confidence is metadata only.
- Accepted claims require typed support.
- Rejected and abstained claims preserve failure evidence.

## Non-claims

- not AGI
- not a general theorem prover
- not broad natural-language understanding
- not a chatbot
- not a replacement for LLMs
- no TensionLM runtime integration in v3.0
