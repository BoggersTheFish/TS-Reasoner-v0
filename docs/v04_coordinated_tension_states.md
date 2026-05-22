# v0.4 Coordinated Tension-State Operation Engine

v0.4 upgrades the trace contract from one scalar tension score to a small
multi-state tension field. The base ranker still computes readable local issues,
but those issues are now interpreted by specialist constraint agents and
propagated through an explicit coupling matrix.

```text
candidate chain
  -> CIG check
  -> base tension score
  -> specialist tension agents
  -> coupling matrix
  -> coordinated tension field
  -> operation router
  -> repaired candidate state
  -> residual trace
```

This keeps v0 inspectable. There is no chatbot-style agent debate and no hidden
state mutation. Each agent reads the same chain/CIG/tension state and emits a
small JSON-compatible signal:

```json
{
  "channel": "logic",
  "tension": 0.5,
  "suspect_edges": ["s1"],
  "suggested_ops": ["CHECK_ENTAILMENT", "LOCALIZE_FAILURE"],
  "confidence": 0.725,
  "shares_with": ["repair", "goal"]
}
```

## Minimum Viable Agents

- `LogicTensionAgent` watches invalid transitions, unsupported conclusions,
  contradictions, circularity, quantifier jumps, and missing premises.
- `GoalTensionAgent` watches whether the selected answer remains unstable under
  the requested goal.
- `RepairTensionAgent` converts repairable issue mass into patch pressure and
  operation hints.
- `CompressionTensionAgent` watches bloat pressure from duplicate claims,
  dependency-free non-premise steps, and overlong traces.

## Coupling

The v0.4 default coupling matrix is deterministic:

```json
{
  "logic": {
    "repair": 0.9,
    "goal": 0.7
  },
  "goal": {
    "repair": 0.6,
    "logic": 0.2
  },
  "repair": {
    "goal": 0.2
  },
  "compression": {
    "goal": 0.4,
    "repair": 0.2
  }
}
```

The coordinator computes:

```text
T_next = T_raw + C * T_raw
```

and caps each coordinated channel at `1.0`. This turns local specialist signals
into a global pressure field.

## Closed Loop

`OperationRouter` applies one bounded transition per candidate:

```text
coordinated field -> selected op -> repair suggestion -> repaired chain -> verifier rescore
```

The transition is accepted only when the repaired chain does not increase global
tension. This keeps v0.4 deterministic and auditable while proving the TS loop
can move from pressure detection to state change.

## Trace Fields

`TSReasoner.run()` now includes:

- `trace.tension_coordinator`
- `trace.coordinated_tension_field`
- `trace.operation_loop`
- `trace.candidate_operation_loops`
- `trace.candidate_scores[*].coordinated_tensions`
- `trace.candidate_scores[*].selected_next_op`
- `trace.candidate_scores[*].post_loop_global_tension`
- `trace.candidate_scores[*].post_loop_status`

The existing top-level fields remain unchanged:

- `selected_chain`
- `tension_score`
- `cig_check`
- `repairs`
- `final_answer`

## Why This Matters

A weighted loss only adds errors together. Coordinated TS routing preserves the
shape of the instability:

```text
logic pressure can wake repair and goal pressure
goal pressure can wake repair and logic pressure
compression pressure can wake goal and repair checks
```

That is the bridge from one reasoner to a TS-native control loop:

```text
pressure -> coordination -> operation -> state change
```
