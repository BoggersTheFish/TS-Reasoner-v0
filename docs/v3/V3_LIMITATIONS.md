# TS-Reasoner v3.0 Limitations

v3.0 is intentionally bounded.

## Current limitations

- Small verifier-derived dataset.
- Synthetic and benchmark-derived candidate rows.
- Linear inspectable model.
- No TensionLM runtime loaded.
- No broad natural-language understanding claim.
- No general theorem-proving claim.
- No guarantee outside the bounded candidate-status task.
- Active-learning challenge rows are controlled, not open-world adversarial samples.

## Safety boundary

The model predicts. The verifier decides.

```text
model prediction ≠ proof
typed verifier support = proof boundary
```

## What would strengthen future versions

- Larger heldout benchmark sets.
- External reasoning benchmarks mapped into typed verifier traces.
- Stronger adversarial candidate generation.
- TensionLM candidate integration as proposal source only.
- More typed verifier channels.
- More varied natural-language claim ingestion.
