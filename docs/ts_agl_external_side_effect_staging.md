# TS-AGL External Side-Effect Staging Arena

v16.0.0 adds a bounded external side-effect staging arena.

The arena proves the highest-risk TS-AGL operation class can be represented and gated:

```text
external_side_effect TSCall
  -> staged as pending
  -> blocked without confirmation
  -> blocked with wrong confirmation
  -> confirmed dry-run dispatch
  -> receipt
Commands
python3 scripts/evaluate_ts_agl_external_side_effect_staging.py
python3 scripts/run_ts_agl_external_side_effect_arena.py
Boundary

This is not real external automation yet.

The v16.0 arena is intentionally bounded:

no external LLM
no real network call
dry-run adapter only
missing or wrong confirmation is blocked
confirmed dispatch is traceable
language is not proof authority
candidate graph contamination remains zero
Release claim

v16.0.0 proves TS-AGL can safely stage and confirm an external_side_effect operation class before any real external adapter is allowed.
