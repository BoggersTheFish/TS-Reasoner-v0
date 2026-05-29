# v4.1 External JSONL Backend Proof

v4.1 proves the optional external JSONL backend path introduced in v4.0.

The live proposer sandbox can load externally emitted candidate claims from JSONL, route them through the backend interface, and still require typed verifier support before acceptance.

## Why this matters

This is the bridge toward v5.0 GPT-2 comparison.

GPT-2 outputs can later be stored as external candidate rows and evaluated through the same verifier-first path.

## What is tested

The v4.1 receipt runs:

    python3 scripts/v4_0/run_live_proposer_sandbox_v40.py \
      --external-jsonl-backend data/v4_1_external_jsonl_backend_proof/external_backend_candidates_v41.jsonl

## Gates

    backend_kind == external_jsonl
    backend_contract_validity == 1.0
    wrong_accept_count == 0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    provenance_preservation_rate == 1.0
    trace_schema_validity == 1.0
    confidence_is_not_proof == true
    live_tensionlm_runtime_loaded == false
    production_runtime_claim == false

## Non-claims

This proves external JSONL backend ingestion only.

This is not GPT-2 comparison yet.

This is not broad NLP.

This is not production runtime integration.

This is not general theorem proving.

Confidence remains metadata.

Typed verifier support remains proof authority.
