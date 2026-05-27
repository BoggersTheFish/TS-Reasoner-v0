# TensionLM Export Set Evaluation

v1.6.0 evaluates a small set of real exported TensionLM-side samples through the
existing TS-Reasoner adapter boundary.

Hard rule:

```text
Do not load TensionLM inside TS-Reasoner.
Do not train anything.
Do not let model confidence become proof.
Do not let candidate edges enter proof support.
Use exported JSONL only.
```

Source evidence comes from an existing TensionLM-side eval artifact:

- repository: `/home/boggersthefish/BoggersSpace/bozo`
- source artifact:
  `/home/boggersthefish/BoggersSpace/bozo/logs/eval/117m_transitivity_seed42.json`
- checkpoint recorded by the source artifact:
  `checkpoints/117m-curriculum/pytorch_model.pt`

The JSONL set preserves TensionLM-side raw completions in `raw_text`. The
`claim` field is the export-side normalized candidate claim passed into
TS-Reasoner unchanged. The evaluator records accepted, rejected, abstained, and
malformed candidates, plus per-sample failure reasons.

Run:

```bash
python3 scripts/evaluate_tensionlm_export_set.py
```

Outputs:

- `artifacts/tensionlm_export_set_report.json`
- `artifacts/tensionlm_export_set_receipt.json`

Metrics:

- `export_set_read_success_rate`
- `candidate_parse_success_rate`
- `provenance_preservation_rate`
- `accepted_outputs_typed_support_rate`
- `bad_candidate_rejection_rate`
- `verifier_beats_confidence_rate`
- `candidate_graph_contamination_count`
- `trace_schema_validity`
- `per_sample_failure_reasons`

Claim level: experimental. v1.6.0 extends the v1.5.0 single-sample bridge into
a small exported set. It does not load TensionLM, train TensionLM, or give model
confidence proof authority.
