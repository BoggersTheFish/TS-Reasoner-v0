# v3.3 External Mini-Benchmark Adapter

v3.3 adds an adapter-shaped external mini-benchmark surface.

This is not an external benchmark victory claim. The goal is narrower:

    Can external-format relation tasks become safe typed verifier traces?

Primary safety metric:

    wrong_accept_count == 0

Secondary gates:

    accepted_without_typed_support_count == 0
    trace_schema_validity == 1.0

The malformed case is preserved and abstained rather than hidden.

## Claim boundary

This release does not claim broad NLP understanding, general theorem proving, or an external benchmark win. It only claims a small adapter smoke test with safe rejection/abstention behaviour.
