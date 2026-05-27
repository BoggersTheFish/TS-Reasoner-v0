# Real TensionLM Candidate Adapter

v1.2.0 adds a narrow adapter for real or exported TensionLM-style candidate
outputs. This adapter consumes exported candidate JSONL. It does not load,
train, or sample TensionLM. It accepts JSONL rows, normalizes model outputs into
the v1.1 candidate bridge contract, and lets TS-Reasoner typed channels remain
the verifier.

Rule:

```text
TensionLM proposes.
Bridge normalizes.
TS-Reasoner verifies.
Typed channels decide.
```

## JSONL Input

Each line has this shape:

```json
{
  "input_text": "All A are B. All B are C. Are all A C?",
  "model": "TensionLM-or-exported-candidate-source",
  "candidates": [
    {
      "claim": "All A are C",
      "confidence": 0.72,
      "provenance": "model_output",
      "raw_text": "A is therefore C"
    }
  ]
}
```

`provenance` becomes the candidate source. Missing provenance is rejected by the
existing bridge boundary. `raw_text`, `model`, and the raw candidate object are
preserved in candidate metadata.

Model confidence remains candidate metadata. It does not create proof authority;
accepted outputs still require typed-channel support.

## Commands

Run the smoke adapter:

```bash
python3 scripts/run_real_tensionlm_candidate_adapter.py
```

Evaluate the contract:

```bash
python3 scripts/evaluate_real_tensionlm_candidate_adapter.py
```

Outputs:

- `artifacts/real_tensionlm_candidate_adapter_smoke.json`
- `artifacts/real_tensionlm_candidate_adapter_report.json`
- `artifacts/real_tensionlm_candidate_adapter_receipt.json`

Success condition:

- exported model outputs enter the existing bridge
- candidate provenance is preserved
- malformed outputs are rejected
- high-confidence bad outputs still lose to typed verification
- accepted outputs require typed-channel support
- trace schema remains valid

Public claim:

TS-Reasoner can safely consume external model candidate outputs through a typed
verification boundary, preserving provenance and preventing candidate confidence
from becoming proof.
