# TS-Reasoner + TensionLM Bridge

The bridge is the first integration point between the public TensionLM runner
and the stable TS-Reasoner v1 trace contract.

```text
TensionLM proposes -> TS-Reasoner verifies -> trace records tension/repair/rejection
```

This does not make TensionLM a proof system. TensionLM only supplies candidate
completion text. TS-Reasoner converts parseable completions into candidate
chains, scores them with the CIG/tension loop, and records whether each neural
proposal was accepted, repaired, or rejected.

## Command

Offline deterministic smoke:

```bash
python3 scripts/run_tensionlm_bridge.py --offline
```

Local public TensionLM checkout:

```bash
python3 scripts/run_tensionlm_bridge.py \
  --tensionlm-path ../TensionLM \
  --repo-id BoggersTheFish/TensionLM-Curriculum-13M \
  --question "If all mammals are animals and all whales are mammals, are all whales animals?" \
  --premise "All mammals are animals." \
  --premise "All whales are mammals."
```

The script writes `artifacts/tensionlm_bridge_smoke.json`.

## Trace Extension

The bridge keeps the v1 top-level schema and adds one optional trace key:

- `trace.neural_generation`

That object records the prompt, raw proposals, parse status, candidate chain id,
initial/post-loop tension, issue kinds, and verifier status.

## Limit

The public TensionLM checkpoint is a raw narrow research checkpoint. Output can
be low quality. The bridge receipt is about reproducibility and verification,
not impressive generation.

Public claim:

> We are testing whether a tension-attention language model can improve an
> inspectable reasoning loop.

Non-claim:

> TensionLM is not presented here as a complete chatbot or standalone proof
> system.
