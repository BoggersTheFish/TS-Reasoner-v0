# v3.7 Real Exported Candidate Batch

v3.7 extends the v3.6 proposer-boundary evaluation from controlled/mock proposer rows into a larger real-export-shaped candidate batch.

## Core claim

    Real exported candidate batches can enter TS-Reasoner as candidate data.
    Typed verifier support remains proof authority.

## What is tested

The v3.7 batch preserves export-shaped fields:

- raw candidate text;
- confidence;
- source;
- provenance export id;
- model hint;
- source file;
- row index.

The evaluator verifies that provenance survives the verifier boundary and that confidence does not become proof.

## Gates

    wrong_accept_count == 0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    provenance_preservation_rate == 1.0
    trace_schema_validity == 1.0
    live_tensionlm_runtime_loaded == false

## Non-claims

This is not live TensionLM runtime integration.

This is not a broad NLP claim.

This is not an external benchmark victory claim.

This is not general theorem proving.

Exported candidates remain candidate data.

Typed verifier channels remain proof authority.
