# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![Tests](https://img.shields.io/badge/tests-unittest_passed-brightgreen)](tests)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-v0_research_release-orange)](model_card.md)

TS-Reasoner-v0 is a standalone toy research release for inspectable reasoning telemetry. It represents reasoning chains as a small constraint graph, scores local failures as tension, and proposes repairs that try to reduce tension.

It is not a downloaded model, transformer, benchmark-grade prover, or production reasoning system. v0 uses deterministic Python standard-library heuristics so every node, edge, issue, and repair can be inspected.

## Why This Matters

TS-Reasoner-v0 is the bridge repo: it turns the TS loop into runnable reasoning telemetry instead of a verbal claim. The core path is:

```text
question -> candidate chains -> CIG checks -> tension issues -> repair suggestions -> selected low-tension answer -> JSON trace
```

That makes the substrate visible before any learned model is plugged in. v0 proves the interface; later versions can learn the generator, tension field, or proof ranker while keeping the same trace contract.

## TS Mapping

- **TS-Core:** reasoning steps are graph nodes and dependencies are support edges.
- **TensionLM:** high-tension local failures are explicit fields, not hidden attention weights.
- **CIG:** extracted claims keep provenance back to source steps and dependencies.
- **Proof Ranker:** candidate chains are selected by lower global tension and higher stability.

The toy loop is: generate candidate chains, extract claims, score local/global tension, suggest repairs, then select the most stable chain.

## Quickstart

```bash
python3 inference.py --question "If all A are B and all B are C, are all A C?"
python3 demo_reasoning.py
python3 -m unittest discover
```

The CLI writes `artifacts/latest_trace.json`. The demo writes:

- `artifacts/sample_outputs.md`
- `artifacts/tension_traces.jsonl`
- `artifacts/eval_summary.json`

## Trace Preview

A compact trace preview is available at `docs/trace_preview.md`. The full CLI trace is written to `artifacts/latest_trace.json`.

## Example Output

```text
TS-Reasoner-v0
Question: If all A are B and all B are C, are all A C?
Answer: all A are C.
Selected chain: candidate_cautious
Global tension: 0.0000
Trace: artifacts/latest_trace.json
```

## Release Hierarchy

```text
TS-Core
  |
  v
TS-Reasoner-v0
  |
  v
TS-Proof-Ranker
  |
  v
TensionProofLM
  |
  v
Full TS-native reasoning model
```

This repo is not the final model. It is the control panel and trace contract for the final model.

## Limitations

- Claim extraction is regex-based and covers only small syllogistic templates.
- The CIG is a toy provenance graph, not a full formal logic engine.
- Contradiction, support, and quantifier checks are heuristic.
- TensionLM generation and trained proof ranking are future interfaces only.
- Artifact metrics are toy-scope receipts, not benchmark claims.

## Roadmap

- **v1:** learned proof/tension ranker while preserving the v0 trace format; broader CIG patterns, better natural-language negation, and richer repair application.
- **v2:** learned TensionLM candidate generation with exported tension fields.
- **v3:** trained proof-ranker integration and grounded trajectory scoring over larger tasks.

## License

MIT. See `LICENSE`.
