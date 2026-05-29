# v3.8 External Benchmark Translation Pack

v3.8 adds a bounded external-format translation pack.

It converts benchmark-shaped multiple-choice relation rows into TS-Reasoner candidate/premise traces.

## Core claim

    External-format reasoning tasks can be translated into typed verifier traces.
    Unsupported candidates are rejected or abstained.
    Answer keys and confidence remain metadata, not proof authority.

## What is preserved

The translator preserves:

- source task id;
- benchmark name;
- raw prompt;
- raw candidates;
- answer key;
- translation metadata.

## Gates

    wrong_accept_count == 0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    source_metadata_preservation_rate == 1.0
    trace_schema_validity == 1.0
    external_benchmark_victory_claim == false
    live_tensionlm_runtime_loaded == false

## Non-claims

This is not an external benchmark victory claim.

This is not broad natural-language understanding.

This is not live TensionLM runtime integration.

This is not general theorem proving.

Benchmark text, answer keys, and confidence remain metadata.

Typed verifier support remains proof authority.
