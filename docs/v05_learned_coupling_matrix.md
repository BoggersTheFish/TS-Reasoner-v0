# v0.5 Residual-Trained Coupling Matrix

v0.5 makes the coupling matrix trainable from v0.4 repair traces. The system
still uses a deterministic standard-library learner, not neural weights.

```text
candidate chain
  -> v0.4 tension agents
  -> operation router
  -> repaired candidate
  -> before/after residual
  -> coupling learner
  -> learned coupling matrix
```

## Training Signal

For each successful one-step repair, the learner records:

- raw source-channel tensions before repair
- coordinated target-channel tensions before repair
- coordinated target-channel tensions after repair
- residual delta per target channel

A source channel earns coupling weight toward a target channel when:

```text
source_raw_tension > 0
target_coordinated_tension_after < target_coordinated_tension_before
```

The learned weight is:

```text
weight(source, target)
  = mean(target_tension_drop | source_raw_tension active)
```

Then the observed weight is blended with the v0.4 default matrix as a weak prior
so sparse toy examples do not erase known TS structure.

## Artifact

Train with:

```bash
python3 scripts/train_coupling_matrix.py
```

This writes:

- `artifacts/learned_coupling_matrix_v05.json`
- `artifacts/learned_coupling_matrix_summary.json`

The artifact has this shape:

```json
{
  "model_type": "residual_coupling_matrix",
  "coupling_matrix": {
    "logic": {
      "goal": 0.8298,
      "repair": 0.9426
    }
  },
  "metadata": {
    "training_source": "synthetic_tasks candidate repair residuals"
  }
}
```

## Runtime

The learned matrix can be loaded directly:

```python
from ts_reasoner import run_reasoner
from ts_reasoner.tension_agents import TensionCoordinator

coordinator = TensionCoordinator.from_json("artifacts/learned_coupling_matrix_v05.json")
output = run_reasoner(question, premises, tension_coordinator=coordinator)
```

or from the CLI:

```bash
python3 inference.py --question "If some A are B and all B are C, are all A C?" \
  --premise "Some A are B." \
  --premise "All B are C." \
  --coupling-matrix artifacts/learned_coupling_matrix_v05.json
```

## Scope

This is not a learned reasoner. v0.5 only learns how tension channels should
wake each other after observing which repairs lowered residual pressure.

