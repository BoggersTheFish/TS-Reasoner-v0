# Messy Language Candidate Stress

v1.3.0 stresses exported candidate ingestion with messy language before any live
model-loading work.

The verifier boundary is unchanged:

```text
TensionLM proposes.
Bridge normalizes messy exported candidates.
TS-Reasoner verifies.
Typed channels decide.
```

This stress covers:

- paraphrased relation claims
- partial claims
- extra irrelevant text
- contradictory candidate sets
- unsupported leaps
- bad or missing confidence
- ambiguous relation wording
- multi-candidate outputs where the wrong candidate has higher confidence

The adapter may normalize relation-shaped paraphrases into canonical candidate
claims such as `All A are C`. It does not treat confidence as proof. Partial and
ambiguous candidates remain malformed and are rejected by the v1.1 bridge
boundary. Accepted outputs still require typed-channel support.

When multiple relation-shaped fragments are present, the adapter selects the
latest parseable candidate fragment under the current exported-output policy.
This is a deterministic ingestion rule, not proof that the system fully
understands arbitrary natural language.

Run the stress:

```bash
python3 scripts/evaluate_messy_language_candidate_stress.py
```

Outputs:

- `artifacts/messy_language_candidate_stress_report.json`
- `artifacts/messy_language_candidate_stress_receipt.json`

Success metrics:

- `messy_candidate_parse_success_rate`
- `bad_candidate_rejection_rate`
- `verifier_beats_confidence_rate`
- `provenance_preservation_rate`
- `candidate_graph_contamination_count`
- `accepted_outputs_typed_support_rate`
- `trace_schema_validity`

Claim level: experimental. TS-Reasoner can robustly ingest messy exported
language-model candidate outputs while preserving provenance and verifier
authority.
