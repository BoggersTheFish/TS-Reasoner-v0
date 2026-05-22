# v0.6 Bounded Multi-Step Tension-Control Loop

v0.6 upgrades operation routing from one transition per candidate to a bounded
control loop.

```text
state
  -> tension agents
  -> coupling matrix
  -> operation router
  -> state transition
  -> verifier rescore
  -> residual
  -> next cycle
```

The loop stops when the candidate settles, reaches an explicit no-op/failure
status, or hits `max_steps`.

## Runtime Trace

Each candidate operation loop includes:

```json
{
  "status": "settled",
  "cycle_count": 2,
  "settled": true,
  "cycles": [
    {
      "cycle": 1,
      "selected_op": "REPAIR_STEP",
      "status": "repaired",
      "before": {},
      "after": {},
      "residual": {}
    },
    {
      "cycle": 2,
      "selected_op": "COMPRESS_TRACE",
      "status": "compressed",
      "before": {},
      "after": {},
      "residual": {}
    }
  ]
}
```

## Operation Handlers

- `ACCEPT_TRACE` stops on a stable state.
- `REPAIR_STEP` applies the best repair suggestion for the active target.
- `COMPRESS_TRACE` removes duplicate non-premise steps when available.
- `LOCALIZE_FAILURE` records localization without mutation.
- `VERIFY_GOAL_SUPPORT` records goal verification or goal instability.

## Hard Loop Cases

`v06_loop_cases()` adds synthetic chains that exercise repeated transitions:

- quantifier jump followed by trace compression
- missing premise plus overconfident forced answer
- contradiction plus forced answer
- circular reasoning repair

## Evaluation

Run:

```bash
python3 scripts/evaluate_v06_loop.py
```

The report is written to `artifacts/v06_loop_eval.json` and includes:

- initial global tension
- final global tension
- cycles used
- settled rate
- failed-to-settle cases

The current v0.6 receipt intentionally records remaining surface tension: one
case reaches zero scalar global tension but still fails to settle because
compression pressure has no valid mutation left. That is a useful next target,
not a hidden pass.

