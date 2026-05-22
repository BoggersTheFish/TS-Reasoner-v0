# v0.8 External Benchmark Harness

v0.8 adds a small externalized benchmark harness around the v0.7 bounded
tension-control loop.

The purpose is not to claim broad reasoning ability. The purpose is to stop
evaluating only repo-native examples and create a repeatable receipt that
compares the control loop against simple baselines on curated prompts normalized
into TS-Reasoner relation form.

## Benchmark Shape

The fixture is `data/external_benchmark_v08.jsonl`.

It contains ten tasks across five categories:

- `syllogism_variant`
- `boolean_word_problem`
- `small_proof_chain`
- `contradiction_detection`
- `repair_needed`

Each task records:

- an external-style prompt,
- normalized TS-Reasoner premises and question,
- acceptable answer strings,
- a category,
- a scope/source note.

## Baselines

Run:

```bash
python3 scripts/evaluate_v08_external_benchmark.py
```

The script writes `artifacts/v08_external_benchmark_report.json` and compares:

- `direct`: first generated candidate.
- `random_selector`: deterministic seeded random candidate.
- `ranker_only`: one-shot heuristic tension ranker, no repair loop.
- `full_control_loop`: v0.7 bounded tension-control loop with the learned v0.5 coupling matrix when available.

## Current Receipt

The current v0.8 report runs ten tasks.

| Baseline | Correct | Accuracy | Mean tension |
| --- | ---: | ---: | ---: |
| `direct` | 4/10 | 0.4000 | 0.2141 |
| `random_selector` | 5/10 | 0.5000 | 0.1771 |
| `ranker_only` | 8/10 | 0.8000 | 0.0767 |
| `full_control_loop` | 8/10 | 0.8000 | 0.0000 |

The full loop settles 10/10 tasks with mean `cycles_used = 1.0`.

## Interpreting The Result

The useful v0.8 result is mixed and inspectable:

- The full loop improves over `direct` and `random_selector`.
- The full loop ties `ranker_only` on answer accuracy.
- The full loop produces lower final mean global tension than all baselines.
- The full loop exposes a clear gap on `small_proof_chain`: it settles to
  low-tension abstentions on both three-hop proof-chain tasks, while the direct
  candidate gets both correct.

That gap is the next real target: the verifier/generator pair needs stronger
transitive proof-chain support before v1 benchmark claims.

## Narrow Claim

TS-Reasoner v0.8 tests whether bounded tension-control improves answer
selection and repair over simpler baselines on externalized small reasoning
tasks. It is still a toy-scope receipt, not a broad benchmark claim.
