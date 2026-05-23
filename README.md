# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-v1_trace_contract-blue)](MODEL_CARD.md)

TS-Reasoner is an inspectable reasoning control loop. It generates candidate
reasoning chains, scores local and global tension, runs a bounded repair or
compression loop, settles a trace, and exposes why a result was accepted or
rejected.

This repository is the stable public v1.0 foundation for that loop. It is not a
large language model, a general theorem prover, or a broad benchmark claim.

## One-Command Run

```bash
python3 inference.py --question "If all A are B and all B are C, are all A C?"
```

That writes `artifacts/latest_trace.json` and prints the selected answer,
selected chain, and global tension.

Run all examples and tests:

```bash
python3 demo_reasoning.py
python3 -m unittest discover
```

## What It Does

The core pipeline is:

```text
input problem
-> candidate chains
-> Claim-Interaction Graph checks
-> local/global tension scoring
-> bounded repair/compression loop
-> selected answer or failure reason
-> JSON trace
```

Tension is a transparent instability score. Local tension marks the step where
support is missing, a contradiction appears, a quantifier jump happens, or a
claim is overconfident. Global tension summarizes the candidate chain.

Traces are the public API of TS reasoning. Every trace records the input,
candidate steps, local tension, global tension, chosen action, rejected
alternatives, settled answer, and failure reason when the loop does not settle.

## v1.0 Receipts

Generate the stable v1 benchmark receipt:

```bash
python3 scripts/evaluate_v1_baseline.py
```

This writes:

- `artifacts/v1_baseline_report.json`
- `artifacts/release_receipt_v1.0.0.json`

Current v1 receipt:

- `20` tasks total.
- `16` expected-pass tasks.
- `4` adversarial known-limit tasks.
- `full_control_loop`: `16/16` on expected-pass tasks.
- Known-limit tasks are included to make failures visible, not to claim solved behavior.

See `BENCHMARKS.md` for the benchmark categories and `LIMITATIONS.md` for the
non-claims.

## TensionLM Bridge

TS-Reasoner can use TensionLM as an optional candidate proposer while keeping
TS-Reasoner as the verifier:

```text
problem
-> TS-Reasoner reasoning state
-> TensionLM proposes candidate text
-> tension scorer and verifier evaluate it
-> trace records acceptance, repair, or rejection
```

Run the offline bridge smoke receipt:

```bash
python3 scripts/run_tensionlm_bridge.py --offline
```

Run against a local public TensionLM checkout:

```bash
python3 scripts/run_tensionlm_bridge.py --tensionlm-path ../TensionLM
```

The bridge writes `artifacts/tensionlm_bridge_smoke.json`. The public claim is
narrow: this tests whether a tension-attention language model can improve an
inspectable reasoning loop.

## TensionProofLM Target

The next model target is `TensionProofLM-22M`: a small model trained for proof
step proposal, repair, and abstention, not general chat.

Run the tiny smoke-training/eval receipt:

```bash
python3 scripts/run_tensionprooflm_smoke.py
```

This writes `artifacts/tensionprooflm_smoke_report.json`. The smoke run validates
the data/eval contract only; it is not a trained 22M checkpoint.

## Public Docs

- `TRACE_SCHEMA.md`: stable JSON trace contract.
- `BENCHMARKS.md`: v1 benchmark suite and receipt shape.
- `LIMITATIONS.md`: explicit known limits and non-claims.
- `MODEL_CARD.md`: intended use, risks, and eval summary.
- `docs/tensionlm_bridge.md`: optional TensionLM proposal bridge.
- `docs/tensionprooflm_22m.md`: next model target and metric.

## Installation

No runtime dependencies are required beyond Python 3.10+.

```bash
python3 -m unittest discover
python3 inference.py --question "If all cats are mammals and all mammals are animals, are all cats animals?"
```

The package also exposes a console entry point when installed:

```bash
ts-reasoner --question "If all A are B and all B are C, are all A C?"
```

## Claim Boundary

TS-Reasoner v1.0 claims:

- stable inspectable traces,
- deterministic small reasoning receipts,
- visible failure modes,
- a bridge contract for learned candidate proposers.

TS-Reasoner v1.0 does not claim:

- general reasoning ability,
- production decision-making reliability,
- formal proof completeness,
- chatbot quality,
- superiority over frontier models.
