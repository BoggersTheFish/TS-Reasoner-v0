# Proof Objects

v28.0.0 makes typed verifier support visible.

Run:

```bash
python3 scripts/show_proof_object_examples.py
```

Output:

- `artifacts/proof_object_examples.json`

Each proof example includes:

- `claim`
- `normalized_claim`
- `support_path`
- `typed_channel`
- `verifier_decision`
- `why_accepted_rejected_or_abstained`
- `model_confidence`
- `confidence_ignored`
- `support_object`
- `trace_hash_valid`

The point is direct: confidence can be high and still ignored. Acceptance comes from typed verifier support.
