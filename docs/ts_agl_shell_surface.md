# TS-AGL Shell Surface

v22.0.0 adds a speakable shell surface for TS-AGL.

The shell exposes the current bounded operator stack through one command surface:

```bash
python3 -m ts_agl.shell "inspect project and stage next safe note"
python3 -m ts_agl.shell "route: is the repo clean?"
python3 scripts/run_ts_agl_shell_surface.py "help"
What it can do
show shell help
route a command through the router stack
run the local project operator
write a receipt for the shell invocation
Boundary

This is not broad autonomous agency.

The v22.0 shell is intentionally bounded:

no external LLM
no real external side effects
shell output is not proof authority
route confidence is not proof
local writes remain confirmation-gated through the operator stack
candidate graph contamination remains zero
Release claim

v22.0.0 turns TS-AGL from internal scripts into a speakable shell surface over the current router/operator stack.
