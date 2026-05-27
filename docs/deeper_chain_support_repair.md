# Deeper-Chain Support Repair

v1.7.0 repairs the deeper-chain support gap preserved by the v1.6.0 export set
receipt.

The repair is structural:

```text
All A are B
All B are C
All C are D
candidate: All A are D
  -> typed transitivity closes the support chain
  -> candidate accepted with typed support
```

Boundary:

- No TensionLM loading inside TS-Reasoner.
- No training.
- No confidence-as-proof.
- No candidate edges entering proof support.

Run:

```bash
python3 scripts/evaluate_deeper_chain_support_repair.py
```

Outputs:

- `artifacts/deeper_chain_support_repair_report.json`
- `artifacts/deeper_chain_support_repair_receipt.json`

Metrics:

- `deeper_chain_acceptance_rate`
- `wrong_reverse_rejection_rate`
- `identity_collapse_count`
- `candidate_graph_contamination_count`
- `trace_schema_validity`
- `v1_6_failure_repair_rate`

Claim level: experimental. This repairs positive all/all deeper-chain support
inside the verifier boundary. It does not expand TensionLM authority.
