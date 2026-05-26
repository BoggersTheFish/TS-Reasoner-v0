# Typed Tension Traces: TS-Core-backed Channel Reasoning

TS-Reasoner now has a TS-Core-backed typed tension path alongside the existing public trace contract.

The core shift is from one scalar tension surface toward channel-specific operational traces:

```text
question
-> candidate chains
-> CIG checks
-> TS-Core graph adapter
-> typed tension channels
-> resolver events
-> answer + trace
```

## What The Trace Shows

Each run emits:

- `trace.tension_channels`: per-channel activation, initial tension, resolution, final tension, evidence, and details.
- `trace.typed_runtime`: settlement state, typed global tension, resolver events, and context updates such as blocked edges or blocked equalities.

Core bullet:

> The system now emits per-channel reasoning traces, showing which typed tensions activated, how they resolved, and whether the answer settled.

## Tiny Demo

Input:

```text
All A are B.
All B are C.
Question: Are all A C?
```

Typed settlement:

- `logic_transitivity` activates and adds inferred edge `A -> C`.
- `surface_structure` tags `A -> C` as inferred, not directly stated.
- `identity_preservation` blocks `A = C`.
- `directionality` blocks unsupported `C -> A`.

Expected answer:

```text
all A are C.
```

The point is not that this solves general reasoning. The point is that the proof-chain completion, reverse-edge block, and identity-collapse block are separate inspectable channels rather than one hidden score.

## Run It

```bash
python3 scripts/demo_typed_tension.py
python3 scripts/evaluate_typed_tension.py
```

Generated artifacts:

- `artifacts/typed_tension_demo.json`
- `artifacts/typed_tension_benchmark_report.json`
- `artifacts/typed_tension_receipt.json`

## Current Scope

This is deterministic and toy-scope:

- Regex-style relation parsing.
- Curated syllogistic examples.
- Hand-coded channel resolvers.
- No learned calibrator yet.
- No TensionLM bridge in this release.

The next experiment should train a tiny typed-channel calibrator over channel activation, weights, and resolver priority.
