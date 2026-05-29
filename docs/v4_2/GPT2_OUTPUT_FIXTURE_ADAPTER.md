# v4.2 GPT-2 Output Fixture Adapter

v4.2 adds a GPT-2-shaped output fixture adapter.

It converts GPT-2-style generated text rows into external JSONL candidate rows for the v4 live proposer sandbox.

## Why this matters

This prepares the v5.0 GPT-2 comparison target.

GPT-2 outputs can now be represented as candidate data in the same external backend format proven by v4.1.

## Pipeline

    GPT-2-style output fixture
      -> adapted external JSONL candidate row
      -> live proposer sandbox external_jsonl backend
      -> typed verifier gate
      -> accept / reject / abstain

## Gates

    adapter_success_rate == 1.0
    backend_kind == external_jsonl
    backend_contract_validity == 1.0
    wrong_accept_count == 0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    provenance_preservation_rate == 1.0
    trace_schema_validity == 1.0
    gpt2_comparison_claim == false
    confidence_is_not_proof == true

## Non-claims

This is a GPT-2 output fixture adapter only.

This is not a live GPT-2 runner.

This is not GPT-2 comparison yet.

This is not broad NLP.

This is not general theorem proving.

Model fluency and confidence remain metadata.

Typed verifier support remains proof authority.
