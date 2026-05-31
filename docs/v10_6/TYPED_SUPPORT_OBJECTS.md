# TS-Reasoner v10.6.0: Typed Support Objects

v10.6 replaces symbolic support strings with typed, hash-checked verifier
support objects.

Acceptance requires:

- `support_type == typed_verifier_trace`
- `claim == support.derived_claim`
- `support.verifier_passed == true`
- `support.channel` is allowed
- `support.trace_hash` matches the canonical support payload

The release gate is `python3 scripts/v10_6/evaluate_typed_support_objects.py`.
It writes `artifacts/typed_support_objects_report.json` and
`artifacts/typed_support_objects_receipt.json`.
