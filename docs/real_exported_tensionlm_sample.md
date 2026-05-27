# Real Exported TensionLM Sample

v1.5.0 evaluates a real exported TensionLM-side sample through the existing
TS-Reasoner adapter.

Hard rule:

```text
Do not load TensionLM inside TS-Reasoner.
Do not train anything.
Do not let model confidence become proof.
Use exported JSONL only.
```

Source evidence comes from an existing TensionLM-side eval artifact:

- repository: `/home/boggersthefish/BoggersSpace/bozo`
- source artifact:
  `/home/boggersthefish/BoggersSpace/bozo/logs/eval/117m_transitivity_seed42.json`
- checkpoint recorded by the source artifact:
  `checkpoints/117m-curriculum/pytorch_model.pt`

The JSONL sample preserves the TensionLM-side raw completion in `raw_text`.
The `claim` field is the export-side normalized candidate claim passed into
TS-Reasoner unchanged. TS-Reasoner verifies that candidate through the existing
v1.3 adapter and typed-channel boundary.

Run:

```bash
python3 scripts/evaluate_real_exported_tensionlm_sample.py
```

Outputs:

- `artifacts/real_exported_tensionlm_sample_report.json`
- `artifacts/real_exported_tensionlm_sample_receipt.json`

Metrics:

- `sample_read_success_rate`
- `candidate_parse_success_rate`
- `provenance_preservation_rate`
- `accepted_outputs_typed_support_rate`
- `bad_candidate_rejection_rate`
- `verifier_beats_confidence_rate`
- `candidate_graph_contamination_count`
- `trace_schema_validity`

Claim level: experimental. This is the first real cross-repo exported sample
proof: real exported TensionLM-side candidate data can cross into TS-Reasoner
while remaining candidate data, not proof.
