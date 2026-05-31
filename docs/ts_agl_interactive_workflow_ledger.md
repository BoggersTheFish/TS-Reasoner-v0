# TS-AGL Interactive Workflow Ledger

v15.0.0 adds a bounded interactive workflow ledger for TS-AGL.

The ledger proves a multi-turn action pattern:

```text
stage pending action
  -> block missing confirmation
  -> block wrong confirmation
  -> execute with correct confirmation
  -> preserve event ledger and receipt
Commands
python3 scripts/evaluate_ts_agl_interactive_workflow_ledger.py
python3 scripts/run_ts_agl_interactive_workflow_arena.py
Boundary

This is not broad autonomous agency.

The v15.0 arena is intentionally bounded:

no external LLM
reversible write only
write target restricted through the filesystem adapter
pending action requires confirmation token
missing or wrong confirmation is blocked
confirmed execution is traceable
language is not proof authority
candidate graph contamination remains zero
Release claim

v15.0.0 moves TS-AGL from single-step confirmed action into a replayable workflow ledger with pending action state and confirmation over time.
