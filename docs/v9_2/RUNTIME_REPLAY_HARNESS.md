# TS-Reasoner v9.2.0: Runtime Replay Harness

v9.2.0 adds a bounded runtime replay harness.

The purpose is to process ordered multi-event sessions through the verifier-first runtime kernel.

## What v9.2.0 adds

- JSONL replay cases
- ordered event replay
- per-event kernel receipt collection
- final state audit
- multi-event contamination gate
- replay evaluator receipt

## What v9.2.0 proves

The runtime kernel can process multi-event sessions while preserving event order and keeping candidate graph contamination at zero.

## Boundary

Replay is not proof.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
