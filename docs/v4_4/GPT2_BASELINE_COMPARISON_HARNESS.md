# v4.4 GPT-2 Baseline Comparison Harness

v4.4 adds the first bounded GPT-2 baseline comparison harness.

It compares TS-Reasoner's bounded natural-language reasoning shell against GPT-2-shaped baseline answer fixtures.

## Why this matters

This is the direct runway to v5.0.

v4.2 created the GPT-2 output fixture adapter.

v4.3 created the natural-language reasoning shell.

v4.4 connects them into a comparison harness.

## Pipeline

    bounded natural-language prompt
      -> TS-Reasoner natural-language shell
      -> typed verifier answer

    same prompt
      -> GPT-2-shaped baseline output fixture
      -> parsed baseline answer

    comparison harness
      -> accuracy, wrong accepts, abstention, trace receipt

## Gates

    ts_wrong_accept_count == 0
    ts_accepted_without_typed_support_count == 0
    ts_candidate_graph_contamination_count == 0
    trace_schema_validity == 1.0
    gpt2_comparison_claim_is_bounded == true
    broad_gpt2_superiority_claim == false
    confidence_is_not_proof == true

## Non-claims

This is a bounded GPT-2 baseline comparison harness.

This is not a live GPT-2 runner yet.

This is not broad GPT-2 superiority.

This is not broad NLP.

This is not general theorem proving.

Confidence and fluency are not proof.

Typed verifier support remains proof authority.
