# Model Card: TS-Reasoner-v0

## System

TS-Reasoner is a deterministic inspectable reasoning control loop. It generates
candidate chains, scores local/global tension, runs bounded repair or
compression, and emits JSON traces explaining accepted and rejected results.

## Intended Use

- Inspecting small reasoning traces.
- Debugging candidate steps, local tension, global tension, and repair choices.
- Producing deterministic benchmark receipts for narrow symbolic and
  normalized natural-language reasoning tasks.
- Testing learned candidate proposers, such as TensionLM, behind the same trace
  contract.

## Out-of-Scope Use

- Legal, medical, financial, safety-critical, or production decisions.
- General theorem proving.
- Broad benchmark claims.
- Chatbot replacement.
- Claims that TensionProofLM-22M has been trained or released.
- Claims that the v2.0 learned candidate model is an instruction model,
  chatbot, verifier, or proof authority.

## Architecture

The v1.0 loop uses:

- deterministic candidate generation,
- regex relation extraction,
- a toy Claim-Interaction Graph checker,
- heuristic tension scoring,
- specialist tension channels,
- a bounded operation router,
- repair/compression templates,
- JSON trace receipts.

The optional TensionLM bridge adds neural proposal text, but TS-Reasoner remains
the verifier. The TensionProofLM smoke path validates the future proof-step
data/eval contract only.

v2.0.0 adds a tiny pure-Python learned candidate model. It ranks candidate
claims and predicts typed-channel/resolver signals from structured graph
features. TS-Reasoner typed channels still verify every candidate before
acceptance.

## Eval Summary

Run:

```bash
python3 scripts/evaluate_v1_baseline.py
```

Current v1.0 receipt:

- `20` tasks total.
- `16` expected-pass tasks.
- `4` adversarial known-limit tasks.
- `full_control_loop`: `16/16` on expected-pass tasks.

Run bridge and target smokes:

```bash
python3 scripts/run_tensionlm_bridge.py --offline
python3 scripts/run_tensionprooflm_smoke.py
```

Run the learned candidate model receipt:

```bash
python3 scripts/build_learned_candidate_dataset.py
python3 scripts/train_learned_candidate_model.py
python3 scripts/evaluate_learned_candidate_model.py
python3 scripts/demo_learned_candidate_model.py
```

## Limitations

The parser is narrow and regex-based. The CIG is inspectable telemetry, not full
formal semantics. The benchmark suite is curated and toy-scope. Neural proposal
quality is not claimed. Known-limit tasks are committed to show where the system
still fails.

## License

MIT.

## Citation

```bibtex
@software{boggersthefish_ts_reasoner_v0,
  title = {TS-Reasoner-v0},
  author = {BoggersTheFish},
  year = {2026},
  license = {MIT}
}
```
