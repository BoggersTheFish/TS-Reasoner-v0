# TS-AGL Controlled External Adapter Gate

v24.0.0 adds a controlled external adapter gate.

The gate proves TS-AGL can safely handle the dangerous boundary before TS-OS v1:

```text
external adapter request
  -> confirmation required
  -> dry-run default
  -> live mode blocked unless TS_AGL_ALLOW_EXTERNAL_LIVE=1
  -> live gate authorization is not execution
  -> no network call performed by the gate
  -> receipt
Commands
python3 scripts/evaluate_ts_agl_external_adapter_gate.py
python3 scripts/run_ts_agl_external_adapter_gate.py
Boundary

This is not live external automation.

The v24.0 gate is intentionally bounded:

no external LLM
no network call
no real external side effect
missing/wrong confirmation is blocked
live mode is blocked unless TS_AGL_ALLOW_EXTERNAL_LIVE=1
env-unlocked live mode only authorizes a downstream adapter; this gate does not execute it
candidate graph contamination remains zero
Release claim

v24.0.0 proves the final safety boundary needed before TS-OS v1: external adapter access is dry-run by default, confirmation-gated, env-gated for live mode, and receipted.
