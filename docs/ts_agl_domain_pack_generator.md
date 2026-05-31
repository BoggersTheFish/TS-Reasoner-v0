# TS-AGL Domain Pack Generator

v17.0.0 adds a bounded domain-pack generator for TS-AGL.

The generator converts structured teaching input into a validated TS-AGL domain pack:

```text
DomainTeachingSpec
  -> generated manifest
  -> manifest validation
  -> example-router compatibility check
  -> receipt
Commands
python3 scripts/run_ts_agl_domain_pack_generator.py
python3 scripts/evaluate_ts_agl_domain_pack_generator.py
Boundary

This is not broad autonomous domain learning.

The v17.0 generator is intentionally bounded:

no external LLM
structured teaching input only
generated packs must pass the existing manifest validator
risky generated operations must require confirmation
generated examples are tested through the example router
language remains an operation interface, not proof authority
candidate graph contamination remains zero
Release claim

v17.0.0 proves TS-AGL can create a new teachable domain pack from structured teaching input and verify that the generated pack can teach routing behavior.
