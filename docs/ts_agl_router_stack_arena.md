# TS-AGL Router Stack Arena

v20.0.0 adds a router stack arena for TS-AGL.

The arena compares:

- rule parser routing
- domain-example routing
- tiny learned routing

Then a safe selector chooses a route or abstains.

## Command

```bash
python3 scripts/evaluate_ts_agl_router_stack_arena.py
Boundary

This is not proof authority.

The v20.0 router stack is intentionally bounded:

no external LLM
no external side effect
learned confidence is not proof
selected calls still go through TSCall
risk gates/adapters/verifier boundaries remain downstream
hard negatives must abstain to route_unknown
candidate graph contamination remains zero
Release claim

v20.0.0 proves TS-AGL can arbitrate between symbolic, example-based, and learned routing while preserving safe abstention and the proof boundary.
