# v2.5.0: Benchmark Harness

v2.5.0 adds a reusable benchmark harness for TS-Reasoner.

The goal is to move from one-off release evaluators to a repeatable benchmark surface with train/dev/test-style splits.

## Benchmark files

```text
data/benchmarks/
  syllogism_train.jsonl
  syllogism_dev.jsonl
  syllogism_test.jsonl
  rule_deduction_train.jsonl
  rule_deduction_dev.jsonl
  rule_deduction_test.jsonl
  adversarial_invalid_test.jsonl
What the harness measures

The v2.5 harness reports:

status accuracy
claim accuracy
parse success rate
invalid rejection-or-abstention rate
accepted-without-typed-support count
candidate graph contamination count
trace schema validity
split-level metrics
category-level metrics
Command
python3 scripts/evaluate_benchmark_harness.py

Generated artifacts:

artifacts/benchmark_harness_report.json
artifacts/benchmark_harness_receipt.json
Boundary

This is not an external benchmark victory claim.

It is a reusable bounded benchmark harness over syllogism, rule-deduction, and adversarial-invalid reasoning surfaces.

The proof boundary remains unchanged:

bounded prompt
→ parser extracts candidate data
→ candidate bridge verifies
→ typed channels decide accept / reject / abstain

No TensionLM runtime is loaded. No neural training is performed.
