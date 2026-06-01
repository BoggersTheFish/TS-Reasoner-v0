# Persistent TS-OS Session Ledger

v23.0.0 adds a persistent TS-OS session ledger over the TS-AGL shell surface.

The ledger persists shell/operator events:

```text
shell command
  -> shell result
  -> session event
  -> saved ledger
  -> reload
  -> replay summary
  -> continue session
Commands
python3 scripts/evaluate_ts_os_session_ledger.py
python3 scripts/run_ts_os_session_ledger.py --reset
python3 scripts/run_ts_os_session_ledger.py "route: is the repo clean?"
Boundary

This is session persistence, not broad autonomous agency.

The v23.0 session ledger is intentionally bounded:

no external LLM
no real external side effects
session replay is not proof authority
shell confidence is not proof
events preserve receipts/payloads rather than silently mutating belief state
candidate graph contamination remains zero
Release claim

v23.0.0 gives the TS-OS runway persistent command memory: shell sessions can be saved, reloaded, replayed, and continued.
