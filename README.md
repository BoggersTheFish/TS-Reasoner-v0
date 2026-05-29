# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v3.6.0-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v3.6.0)

TS-Reasoner is a verifier-first reasoning system.

Core line:

    LLMs propose.
    TS verifies.
    Confidence is not proof.
    Typed traces show why.

It separates candidate generation, learned/advisory ranking, typed proof verification, and traceable rejection or abstention.

    candidate proposer
    -> learned/advisory ranking
    -> typed verifier channels
    -> accept / reject / abstain trace
    -> receipt

## Current flagship release

Current release:

https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v3.6.0

v3.6.0 scales the proposer/verifier boundary from a tiny smoke test into a 12-case adversarial candidate-proposal evaluation.

It adds:

- v3.1 public surface artifact
- v3.2 cold-reader demo trace
- v3.3 external mini-benchmark adapter
- v3.4 verifier-first reasoning draft
- v3.5 TensionLM proposer boundary
- v3.6 scaled proposer boundary evaluation

## Flagship evidence

v3.3 external adapter:

    status_accuracy: 1.0
    wrong_accept_count: 0
    accepted_without_typed_support_count: 0
    trace_schema_validity: 1.0

v3.6 scaled proposer-boundary evaluation:

    case_count: 12
    verifier_selection_accuracy: 1.0
    confidence_top_accuracy: 0.0
    verifier_overrode_confidence_count: 12
    wrong_accept_count: 0
    accepted_without_typed_support_count: 0
    candidate_graph_contamination_count: 0
    live_tensionlm_runtime_loaded: false

Interpretation:

Across 12 adversarial proposer cases, confidence selects the wrong candidate every time while TS-Reasoner still selects or abstains according to typed support.

## Run the current receipts

    python3 scripts/v3_2/run_cold_reader_demo.py
    python3 scripts/v3_3/evaluate_external_minibench_v33.py
    python3 scripts/v3_5/evaluate_tensionlm_proposer_boundary_v35.py
    python3 scripts/v3_6/evaluate_scaled_proposer_boundary_v36.py
    python3 -m unittest discover -q

## What this is

TS-Reasoner is:

- a bounded verifier-first reasoning artifact;
- a typed trace system;
- a candidate rejection and abstention system;
- a safe bridge for learned or language-model candidate proposers;
- a receipt-first research surface for verifier-first reasoning.

## What this is not

TS-Reasoner is not:

- a chatbot;
- a general theorem prover;
- a broad natural-language understanding system;
- an external benchmark victory claim;
- live TensionLM runtime integration;
- a system where model confidence becomes proof authority.

## Why this matters

Language models often entangle candidate generation, confidence, and proof.

TS-Reasoner keeps those roles separate.

A model may propose or rank a candidate claim, but the claim is not accepted unless typed verifier channels support it.

## Core boundary

    candidate generation != proof
    model confidence != proof
    typed verifier support = proof boundary

## Key v3.5 files

- `docs/v3_1/PUBLIC_SURFACE.md`
- `examples/cold_reader_demo/readable_trace.md`
- `docs/v3_3/EXTERNAL_MINIBENCH_ADAPTER.md`
- `docs/v3_4/VERIFIER_FIRST_REASONING_DRAFT.md`
- `docs/v3_5/TENSIONLM_PROPOSER_BOUNDARY.md`
- `docs/v3_6/SCALED_PROPOSER_BOUNDARY.md`

## Release ladder

| Version | Core addition | Boundary |
|---|---|---|
| v1.x | typed tension channels and TensionLM candidate bridge | TensionLM output remains candidate data |
| v2.x | learned candidate models and verifier-trace training | learned models remain advisory |
| v3.0 | verifier-guided candidate model | typed verifier remains proof authority |
| v3.5 | public surface, cold demo, external adapter, proposer boundary | confidence is not proof |
| v3.6 | scaled proposer boundary evaluation | high-confidence candidates remain candidate data |

## One-command baseline

    python3 inference.py --question "If all A are B and all B are C, are all A C?"

That writes `artifacts/latest_trace.json` and prints the selected answer, selected chain, and global tension.
