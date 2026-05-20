# JSON Trace Preview

This preview shows the shape of the inspectable telemetry produced by:

```bash
python3 inference.py --question "If all A are B and all B are C, are all A C?"
```

The complete trace is written to `artifacts/latest_trace.json`.

```json
{
  "question": "If all A are B and all B are C, are all A C?",
  "premises": [
    "all A are B",
    "all B are C"
  ],
  "final_answer": "all A are C.",
  "selected_chain": {
    "chain_id": "candidate_cautious",
    "steps": [
      {
        "step_id": "p1",
        "kind": "premise",
        "text": "all A are B",
        "dependencies": []
      },
      {
        "step_id": "p2",
        "kind": "premise",
        "text": "all B are C",
        "dependencies": []
      },
      {
        "step_id": "s1",
        "kind": "conclusion",
        "text": "Therefore all A are C.",
        "dependencies": ["p1", "p2"]
      }
    ]
  },
  "tension_score": {
    "chain_id": "candidate_cautious",
    "global_tension": 0.0,
    "stability": 1.0,
    "local_tension": {
      "p1": 0.0,
      "p2": 0.0,
      "s1": 0.0
    },
    "issues": []
  },
  "trace": {
    "pipeline": "TS-Reasoner-v0",
    "generator": "DeterministicHeuristicGenerator",
    "selection": {
      "selected_chain_id": "candidate_cautious",
      "criterion": "lowest_global_tension_then_highest_stability"
    },
    "graph_view": {
      "nodes": ["p1", "p2", "s1"],
      "edges": [
        {"from": "p1", "to": "s1"},
        {"from": "p2", "to": "s1"}
      ],
      "claim_count": 3,
      "contradiction_count": 0
    }
  }
}
```

