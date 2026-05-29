# v4.0 Live Proposer Sandbox

v4.0 adds the first bounded live proposer sandbox.

The sandbox calls a proposer backend through a narrow interface, ingests emitted candidate claims, and passes them through the typed verifier boundary.

## Core claim

    A live-proposer sandbox can call a proposer backend through a bounded interface.
    Emitted candidates remain candidate data.
    Typed verifier support is still required before acceptance.

## Backends

The default backend is a fixture backend.

An optional external JSONL backend path is supported for candidate data.

The sandbox does not import, train, or run TensionLM.

## Gates

    live_proposer_sandbox_executed == true
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

This is a sandbox, not production runtime integration.

This is not a broad NLP claim.

This is not an external benchmark victory claim.

This is not general theorem proving.

Confidence remains metadata.

Typed verifier support remains proof authority.
