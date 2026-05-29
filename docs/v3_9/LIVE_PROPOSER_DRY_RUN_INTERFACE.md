# v3.9 Live Proposer Dry-Run Interface

v3.9 adds the final pre-v4 interface layer for live proposer integration.

It does not load TensionLM.

It defines and tests the shape that a live proposer must satisfy before v4.0.

## Core claim

    A live-proposer-shaped interface can emit candidate claims into TS-Reasoner.
    Typed verifier channels remain proof authority.

## Contract

The dry-run proposer must preserve:

- interface name;
- implementation name;
- runtime loaded flag;
- source;
- run id;
- emitted candidate id;
- emitted raw text;
- emitted confidence;
- emission index.

## Gates

    interface_contract_validity == 1.0
    wrong_accept_count == 0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    provenance_preservation_rate == 1.0
    trace_schema_validity == 1.0
    live_tensionlm_runtime_loaded == false
    live_runtime_integration_claim == false
    v4_runtime_contract_ready == true

## Non-claims

This is not live TensionLM runtime integration.

This is not a broad NLP claim.

This is not an external benchmark victory claim.

This is not general theorem proving.

Confidence remains metadata.

Typed verifier support remains proof authority.
