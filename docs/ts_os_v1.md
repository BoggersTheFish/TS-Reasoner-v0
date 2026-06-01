# TS-OS v1

v25.0.0 packages the TS-AGL stack into a bounded TS-OS v1 surface.

TS-OS v1 includes:

- TS-AGL shell surface
- router stack arbitration
- tiny learned router as proposer only
- persistent TS-OS session ledger
- local project operator
- controlled external adapter gate
- release receipts

## Commands

```bash
python3 scripts/evaluate_ts_os_v1.py
python3 scripts/run_ts_os_v1.py
python3 -m ts_agl.os.ts_os_v1
Boundary

TS-OS v1 is not broad autonomous agency.

The v25.0 package is intentionally bounded:

no external LLM
no accidental network call
no real external side effect
language is not proof authority
router confidence is not proof
session replay is not proof authority
external gate authorization is not execution
local writes remain confirmation-gated
candidate graph contamination remains zero
Release claim

v25.0.0 is the first bounded TS-OS v1 package: one operating layer over shell, sessions, routing, local project operation, external adapter gating, and receipts.
