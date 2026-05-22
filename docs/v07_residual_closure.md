# v0.7 Residual Closure

v0.7 closes the residual loop failure exposed by v0.6.

The v0.6 hard eval found a case where scalar global tension reached `0.0`, but
the coordinator still routed to `COMPRESS_TRACE` because a non-premise conclusion
repeated a claim already present in the graph. The old compression handler only
removed exact duplicate steps, so the loop stopped as `no_compression_available`.

v0.7 extends compression to remove redundant non-premise claims:

```text
if a non-premise step's claims are already represented by earlier graph claims,
remove that step and rewrite downstream dependencies
```

## Closed Case

The hard contradiction case now settles as:

```text
REPAIR_STEP      # surface contradiction as instability
REPAIR_STEP      # relax overconfident forced answer
COMPRESS_TRACE   # remove redundant non-premise claim
ACCEPT_TRACE     # stable
```

## Eval

Run:

```bash
python3 scripts/evaluate_v07_loop.py
```

The report is written to `artifacts/v07_loop_eval.json`.

Current result:

```text
hard cases: 4
settled: 4
settled_rate: 1.0
mean_initial_global_tension: 0.4552
mean_final_global_tension: 0.0
```

## Scope

This is still a toy deterministic operation loop. v0.7 does not add a stronger
logic engine. It closes the residual-control gap where an available compression
pressure had no matching graph mutation.

