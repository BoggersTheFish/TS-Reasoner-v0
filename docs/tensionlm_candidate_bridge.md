# TensionLM Candidate Bridge

v1.1.0 starts a narrow bridge between TensionLM-style proposals and
TS-Reasoner typed verification.

Rule:

```text
TensionLM proposes.
TS-Reasoner verifies.
Typed channels decide.
Receipts explain.
```

The bridge does not let TensionLM judge its own output. Candidate claims carry
source and confidence metadata, then verification rebuilds the premise graph
without inserting the candidate as proof support. Typed channels relax that
premise graph and the decision reducer reads the settled channel state.

Minimal flow:

```text
raw text input
  -> candidate bridge
  -> candidate graph claims
  -> TS-Reasoner typed channels
  -> accepted / rejected / abstained candidates
  -> trace receipt
```

## Modes

`mock` is the dependency-light default. It proposes deterministic claims from
simple text patterns:

- the queried relation
- a reverse-relation probe when the subject and predicate differ

`external` is only a hook contract for later TensionLM output. The hook returns
candidate strings, dictionaries, or `CandidateClaim` objects. Model loading is
intentionally outside v1.1.0.

## Decision Contract

Candidate payload:

```json
{
  "input_text": "All A are B. All B are C. Are all A C?",
  "candidate_claims": [
    {
      "candidate_id": "mock_candidate_1",
      "claim": "All A are C",
      "source": "candidate_bridge",
      "confidence": 0.82
    }
  ],
  "verification": {
    "accepted": ["All A are C"],
    "rejected": ["All C are A"],
    "abstained": [],
    "channels": {
      "logic_transitivity": "accepted inferred edge",
      "directionality": "blocked reverse inference"
    }
  }
}
```

Accepted means a typed channel produced or preserved premise support, such as a
`logic_transitivity` inferred edge.

Rejected means a typed channel found a specific blocker, such as
`directionality`, `quantifier_scope`, or `contradiction`.

Abstained means the candidate was parseable but no typed channel supplied support
or a typed rejection.

Malformed candidate claims are rejected before typed verification because they
cannot enter the candidate-graph contract. Candidates with missing source
provenance are also rejected before verification.

## Artifacts

Generate the demo:

```bash
python3 scripts/demo_tensionlm_candidate_bridge.py
```

Evaluate the bridge cases and receipt:

```bash
python3 scripts/evaluate_tensionlm_candidate_bridge.py
```

Run the adversarial bridge stress:

```bash
python3 scripts/evaluate_tensionlm_candidate_bridge_adversarial.py
```

Outputs:

- `artifacts/tensionlm_candidate_bridge_demo.json`
- `artifacts/tensionlm_candidate_bridge_report.json`
- `artifacts/tensionlm_candidate_bridge_receipt.json`
- `artifacts/tensionlm_candidate_bridge_adversarial_report.json`
- `artifacts/tensionlm_candidate_bridge_adversarial_receipt.json`

Success condition:

candidate proposals can enter TS-Reasoner; typed channels can accept, reject, or
abstain; trace receipts preserve candidate provenance; bad candidates are
rejected for typed reasons.

Adversarial success condition:

high-confidence bad proposals do not override typed verification, candidate graph
contamination remains zero, unsupported candidates abstain, malformed candidates
are rejected, and missing provenance is required.
