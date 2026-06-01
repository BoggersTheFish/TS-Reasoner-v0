# TS Evidence Dashboard

v27.0.0 adds one generated evidence artifact:

```bash
python3 scripts/build_ts_evidence_dashboard.py
```

Output:

- `artifacts/ts_evidence_dashboard.json`

The dashboard collects safety metrics across current reports and receipts:

- `wrong_accept_count`
- `accepted_without_typed_support_count`
- `unsafe_request_abstention_rate`
- `destructive_request_block_rate`
- `external_side_effect_performed_count`
- `network_call_performed_count`
- `candidate_graph_contamination_count`
- `confirmed_write_count`
- `unconfirmed_write_block_count`
- `missing_slot_detection_count`
- `external_llm_used`
- `all_gates_passed`

The dashboard includes source provenance so every metric can be traced back to generated repo artifacts.
