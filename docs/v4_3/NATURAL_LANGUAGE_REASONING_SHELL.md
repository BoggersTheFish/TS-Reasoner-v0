# v4.3 Natural-Language Reasoning Shell

v4.3 adds a bounded natural-language reasoning shell.

It extracts simple all/is/are relation premises from natural-language prompts, generates candidate relation claims, verifies those claims through typed support, and renders natural-language answers.

## Pipeline

    natural-language prompt
      -> premise extraction
      -> question extraction
      -> candidate relation claim
      -> typed verifier
      -> natural-language answer

## Gates

    extraction_success_rate == 1.0
    wrong_accept_count == 0
    accepted_without_typed_support_count == 0
    candidate_graph_contamination_count == 0
    trace_schema_validity == 1.0
    gpt2_comparison_claim == false
    broad_nlp_claim == false
    confidence_is_not_proof == true

## Non-claims

This is a bounded natural-language reasoning shell.

This is not GPT-2 comparison yet.

This is not broad NLP.

This is not general theorem proving.

This is not production runtime integration.

Fluency and confidence remain metadata.

Typed verifier support remains proof authority.
