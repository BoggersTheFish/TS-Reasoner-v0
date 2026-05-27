# Live TensionLM Export Smoke

v1.4.0 is an exported-output smoke test. It is not live model integration into
the verifier.

Flow:

```text
external TensionLM-style export
  -> JSONL candidate data
  -> v1.3 exported-output adapter
  -> candidate bridge
  -> TS-Reasoner typed channels
  -> report and receipt
```

Hard boundary:

TensionLM-style outputs remain candidate data and never become proof without
typed-channel support. Confidence remains metadata. Candidate graph
contamination must remain zero.

The included smoke uses deterministic fixture rows with the same shape expected
from an external live/export process. A future branch can replace the fixture
producer with a real exporter without changing the verifier boundary.

Run:

```bash
python3 scripts/run_live_tensionlm_export_smoke.py
python3 scripts/evaluate_live_tensionlm_export_smoke.py
```

Outputs:

- `artifacts/live_tensionlm_export_smoke.json`
- `artifacts/live_tensionlm_export_smoke_report.json`
- `artifacts/live_tensionlm_export_smoke_receipt.json`

Metrics:

- `export_read_success_rate`
- `candidate_parse_success_rate`
- `provenance_preservation_rate`
- `accepted_outputs_typed_support_rate`
- `bad_candidate_rejection_rate`
- `verifier_beats_confidence_rate`
- `candidate_graph_contamination_count`
- `trace_schema_validity`
