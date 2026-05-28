# TS-Reasoner v3.0 Release Gates

v3.0 must not ship because the version number sounds good. It ships only if the model, report, receipt, and demo are stronger than the v2.9 active-learning loop.

## Hard gates

All hard gates must pass:

- status accuracy on heldout eval >= 0.90
- majority baseline margin >= 0.20
- confidence baseline margin >= 0.20
- accepted_without_typed_support_count = 0
- candidate_graph_contamination_count = 0
- trace_schema_validity = 1.0
- model/report/receipt all include boundary metadata
- all tests pass
- release artifacts are reproducible from scripts

## Model-authority gates

The model may:

- rank candidate claims
- predict accepted/rejected/abstained status
- predict likely verifier channels
- provide advisory proposal quality
- help select active-learning rows

The model may not:

- declare proof without typed verifier support
- override verifier rejection
- convert confidence into proof authority
- hide failed channels
- mutate the candidate graph as if its prediction were truth

## Investor-readable gates

The release must be explainable in one sentence:

```text
TS-Reasoner v3.0 is a bounded verifier-guided reasoning model trained from typed verifier traces, with typed channels retained as proof authority.
```

The release must include:

- model card
- limitations
- eval report
- receipt
- local demo command
- release assets

## Delay condition

If v3.0 cannot honestly beat v2.9 on clarity or measured heldout performance, do not ship v3.0. Ship v2.10 instead.
