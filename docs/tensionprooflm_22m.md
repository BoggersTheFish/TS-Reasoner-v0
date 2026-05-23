# TensionProofLM-22M Target

`TensionProofLM-22M` is the next model target after the v1.0 trace-contract
release. It is not a general chatbot target. The intended task is:

```text
input reasoning state -> propose next proof step / repair / abstention
```

TS-Reasoner remains the control loop. A learned model proposes candidate proof
steps or abstention actions; the tension scorer, CIG checker, verifier, and trace
contract decide whether those proposals are accepted, repaired, or rejected.

## Training Data Shape

Use synthetic and small externalized reasoning tasks:

- syllogisms,
- transitive closure,
- graph paths,
- contradiction pairs,
- proof chains,
- candidate repairs,
- invalid proof detection,
- provenance/confidence examples.

Each row should include the reasoning state, target action label, target step
text when applicable, expected local/global tension behavior, and trace fields
needed for inspection.

## Comparisons

Compare against:

- random selector,
- rule baseline,
- softmax transformer same size,
- TensionLM same size,
- ranker-only,
- generator+ranker+verifier loop.

## Metric

The metric is not lower perplexity by itself. The target metric is:

```text
higher correct reasoning steps per parameter with inspectable tension traces
```

## Smoke Receipt

Run:

```bash
python3 scripts/run_tensionprooflm_smoke.py
```

This writes `artifacts/tensionprooflm_smoke_report.json`. The smoke receipt uses
a tiny nearest-centroid proof-step policy to validate the data/eval contract. It
does not train or publish a 22M model.
