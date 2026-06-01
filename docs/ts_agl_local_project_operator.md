# TS-AGL Local Project Operator

v21.0.0 adds a bounded local project operator for TS-AGL.

The operator performs one practical local workflow:

```text
inspect repo
inspect release/tag state
inspect docs folder
use router stack for next safe action
stage a safe artifact write
block unconfirmed write
confirm write
emit project operator receipt
Commands
python3 scripts/evaluate_ts_agl_local_project_operator.py
python3 scripts/run_ts_agl_local_project_operator.py
Boundary

This is not broad autonomous agency.

The v21.0 local project operator is intentionally bounded:

no external LLM
no real external side effects
local repo/filesystem inspection only
reversible artifact write only
unconfirmed write must be blocked
confirmed write must be traceable
router stack is a proposer, not proof authority
candidate graph contamination remains zero
Release claim

v21.0.0 proves TS-AGL can coordinate a practical local project workflow through the current router stack and safety gates.
