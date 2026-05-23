# TS-Reasoner v1.0 Benchmarks

The v1.0 benchmark suite is a small public receipt suite, not a broad reasoning
benchmark. It keeps the v0.8/v0.9 task shape and adds adversarial known-limit
cases so external readers can see both what passes and what still fails.

## Command

```bash
python3 scripts/evaluate_v1_baseline.py
```

This writes:

- `artifacts/v1_baseline_report.json`
- `artifacts/release_receipt_v1.0.0.json`

## Data

The benchmark file is `data/external_benchmark_v1.jsonl`.

Each row contains:

- `id`: stable task id.
- `category`: grouped task category.
- `source`: source or curation tag.
- `external_prompt`: natural-language prompt before normalization.
- `question`: TS-Reasoner question string.
- `premises`: explicit premise list.
- `acceptable_answers`: substrings accepted by the receipt scorer.
- `expected_status`: `expected_pass` or `known_failure`.
- `notes`: narrow reason for inclusion.

## Categories

- `syllogism_variant`
- `boolean_word_problem`
- `small_proof_chain`
- `contradiction_detection`
- `repair_needed`
- `abstention_insufficient`
- `multi_step_symbolic_proof`
- `noisy_candidate_repair`
- `provenance_weighted_reasoning`
- `graph_consistency`
- `refusal_to_settle`
- `adversarial_known_limit`

## Baselines

The report keeps the v0.8 baseline shape:

- `direct`
- `random_selector`
- `ranker_only`
- `full_control_loop`

The headline v1.0 receipt is the `full_control_loop` score split by
`expected_status`. Known-limit tasks are included to make failures visible, not
to claim solved behavior.

## Current Receipt

As of the committed v1.0 receipt:

- `20` tasks total.
- `16` expected-pass tasks.
- `4` adversarial known-limit tasks.
- `full_control_loop`: `16/16` on expected-pass tasks.
- `full_control_loop`: `0/4` on known-limit tasks, by design.

The suite is intentionally small. Its purpose is to prove that small TS systems
can reason with inspectable failure modes, not to compete with broad frontier
model benchmarks.
