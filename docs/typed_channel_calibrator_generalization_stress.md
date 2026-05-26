# Typed-Channel Calibrator Generalization Stress

This stress release tests whether the typed-channel calibrator generalizes beyond the exact trace surface it was trained on.

It does not retrain on the stress set. It loads:

- `artifacts/typed_channel_calibrator.json`
- `data/typed_channel_calibrator_stress.jsonl`

Then it evaluates heldout structures:

- variable renaming
- deeper chains
- distractor premises
- quantifier traps
- contradiction placement
- reverse/identity adversarial queries
- heldout relation shapes
- noisy surface forms

## Run

```bash
python3 scripts/evaluate_typed_channel_calibrator_stress.py
```

Generated artifacts:

- `artifacts/typed_channel_calibrator_stress_report.json`
- `artifacts/typed_channel_calibrator_stress_receipt.json`

## Metrics

- `heldout_answer_accuracy`
- `heldout_channel_activation_accuracy`
- `heldout_resolver_accuracy`
- `depth_generalization_accuracy`
- `distractor_robustness`
- `reverse_fallacy_count`
- `identity_collapse_count`
- `quantifier_trap_failure_count`
- `contradiction_miss_count`
- `trace_schema_validity`

## Honest Outcomes

Outcome A:

```text
Calibrator generalizes cleanly.
Strong evidence that typed trace supervision is reusable.
```

Outcome B:

```text
Calibrator works on renaming but fails deeper chains.
This identifies where the next channel/features need work.
```

Outcome C:

```text
Calibrator overfits current trace surface.
The receipt detects overfit instead of hiding it.
```

TensionLM remains out of scope.
