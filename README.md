# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v3.9.0-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v3.9.0)

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

https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v3.9.0

v3.9.0 adds the final pre-v4 live-proposer dry-run interface: a runtime-shaped contract that emits candidates while typed verifier channels remain proof authority.

It adds:

- v3.1 public surface artifact
- v3.2 cold-reader demo trace
- v3.3 external mini-benchmark adapter
- v3.4 verifier-first reasoning draft
- v3.5 TensionLM proposer boundary
- v3.6 scaled proposer boundary evaluation
- v3.7 real exported candidate batch
- v3.8 external benchmark translation pack
- v3.9 live proposer dry-run interface

## Flagship evidence

v3.3 external adapter:

    status_accuracy: 1.0
    wrong_accept_count: 0
    accepted_without_typed_support_count: 0
    trace_schema_validity: 1.0

v3.9 live proposer dry-run interface:

    input_case_count: 10
    emitted_candidate_count: 18
    interface_contract_validity: 1.0
    verifier_selection_accuracy: 1.0
    confidence_top_accuracy: 0.1
    verifier_overrode_confidence_count: 9
    wrong_accept_count: 0
    accepted_without_typed_support_count: 0
    candidate_graph_contamination_count: 0
    provenance_preservation_rate: 1.0
    live_tensionlm_runtime_loaded: false
    live_runtime_integration_claim: false
    v4_runtime_contract_ready: true

Interpretation:

Across 10 dry-run live-proposer inputs and 18 emitted candidates, TS-Reasoner validates the v4 runtime contract while keeping confidence outside the proof boundary.

## Run the current receipts

    python3 scripts/v3_2/run_cold_reader_demo.py
    python3 scripts/v3_3/evaluate_external_minibench_v33.py
    python3 scripts/v3_5/evaluate_tensionlm_proposer_boundary_v35.py
    python3 scripts/v3_6/evaluate_scaled_proposer_boundary_v36.py
    python3 scripts/v3_7/evaluate_real_exported_candidate_batch_v37.py
    python3 scripts/v3_8/evaluate_external_benchmark_translation_pack_v38.py
    python3 scripts/v3_9/evaluate_live_proposer_dry_run_interface_v39.py
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
- `docs/v3_7/REAL_EXPORTED_CANDIDATE_BATCH.md`
- `docs/v3_8/EXTERNAL_BENCHMARK_TRANSLATION_PACK.md`
- `docs/v3_9/LIVE_PROPOSER_DRY_RUN_INTERFACE.md`

## Release ladder

| Version | Core addition | Boundary |
|---|---|---|
| v1.x | typed tension channels and TensionLM candidate bridge | TensionLM output remains candidate data |
| v2.x | learned candidate models and verifier-trace training | learned models remain advisory |
| v3.0 | verifier-guided candidate model | typed verifier remains proof authority |
| v3.5 | public surface, cold demo, external adapter, proposer boundary | confidence is not proof |
| v3.6 | scaled proposer boundary evaluation | high-confidence candidates remain candidate data |
| v3.7 | real exported candidate batch | provenance survives the proof boundary |
| v3.8 | external benchmark translation pack | answer keys remain metadata, not proof |
| v3.9 | live proposer dry-run interface | v4 runtime contract is ready, but not live yet |

## One-command baseline

    python3 inference.py --question "If all A are B and all B are C, are all A C?"

That writes `artifacts/latest_trace.json` and prints the selected answer, selected chain, and global tension.
