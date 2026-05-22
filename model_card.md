# Model Card: TS-Reasoner-v0

## System

TS-Reasoner-v0 is a deterministic toy reasoning pipeline for inspectable tension telemetry.

## Author

BoggersTheFish.

## License

MIT.

## Intended Use

- Demonstrating constraint-graph reasoning traces.
- Inspecting local tension issues such as quantifier jumps, contradictions, missing premises, unsupported conclusions, and circular reasoning.
- Producing toy repair suggestions for public research discussion.

## Out-of-Scope Use

- Legal, medical, financial, safety-critical, or production decision-making.
- Benchmark claims about general reasoning ability.
- Substitution for a formal theorem prover or a trained language model.

## Architecture

The system uses a deterministic candidate generator, regex claim extraction, a toy Claim-Interaction Graph checker, heuristic tension scoring, specialist tension agents, a coupling matrix, an operation router, repair templates, and a small externalized benchmark harness. v0.5 can load a residual-trained coupling matrix artifact learned from successful repair traces. v0.6 runs bounded multi-step control loops and records cycle-level residuals. v0.7 adds redundant-claim compression to close residual no-op pressure. v0.8 compares direct, random, ranker-only, and full control-loop baselines on curated externalized small-reasoning tasks. No neural model weights are downloaded or executed.

## Eval Summary

Run `python demo_reasoning.py` to regenerate `artifacts/eval_summary.json`. The included demos are toy examples covering valid syllogism, invalid quantifier jump, direct contradiction, missing premise, and repair-loop behavior.

Run `python3 scripts/evaluate_v08_external_benchmark.py` to regenerate `artifacts/v08_external_benchmark_report.json`. The v0.8 fixture has ten curated externalized tasks. Current results are `direct = 4/10`, `random_selector = 5/10`, `ranker_only = 8/10`, and `full_control_loop = 8/10` with `10/10` settled. The full loop currently fails both small proof-chain tasks by settling to low-tension abstentions.

## Limitations

The parser is intentionally narrow. It can miss ordinary-language claims and can over-detect claims inside explanatory text. The scorer is a transparent heuristic, not a calibrated probability model. The v0.8 benchmark fixture is curated and normalized into the system's relation templates, so it should be read as a toy-scope receipt rather than a broad reasoning benchmark.

## Ethical Notes

This release is designed to expose reasoning instability rather than hide it. Outputs should be treated as inspectable telemetry from a toy system, not authoritative answers.

## Citation

Citation placeholder:

```bibtex
@software{boggersthefish_ts_reasoner_v0,
  title = {TS-Reasoner-v0},
  author = {BoggersTheFish},
  year = {2026},
  license = {MIT}
}
```
