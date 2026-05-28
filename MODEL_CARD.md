# Model Card: TS-Reasoner-v0

## System

TS-Reasoner is a deterministic inspectable reasoning control loop. It generates
candidate chains, scores local/global tension, runs bounded repair or
compression, and emits JSON traces explaining accepted, rejected, and abstained
results.

## Intended Use

- Inspecting small reasoning traces.
- Debugging candidate steps, local tension, global tension, typed verifier
  channels, and repair choices.
- Producing deterministic benchmark receipts for narrow symbolic and normalized
  natural-language reasoning tasks.
- Testing learned candidate proposers behind the same trace contract.
- Stress-testing whether model-proposed candidates remain advisory rather than
  proof-authoritative.

## Out-of-Scope Use

- Legal, medical, financial, safety-critical, or production decisions.
- General theorem proving.
- Broad benchmark claims.
- Chatbot replacement.
- Claims that TensionProofLM-22M has been trained or released.
- Claims that the learned candidate model is an instruction model, chatbot,
  verifier, or proof authority.
- Claims that high model confidence can override typed verifier decisions.

## Architecture

The core loop uses:

- deterministic candidate generation,
- regex relation extraction,
- an inspectable Claim-Interaction Graph checker,
- heuristic tension scoring,
- specialist typed tension channels,
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

v2.1.0 adds adversarial stress evaluation for that learned candidate model. The
stress set covers high-confidence wrong candidates, malformed candidates,
unsupported plausible candidates, reverse inference traps, contradiction traps,
identity-collapse traps, distractor-heavy premise sets, and missing-provenance
cases.

## Eval Summary

Run the v1 baseline receipt:

    python3 scripts/evaluate_v1_baseline.py

Run bridge and target smokes:

    python3 scripts/run_tensionlm_bridge.py --offline
    python3 scripts/run_tensionprooflm_smoke.py

Run the learned candidate model receipt:

    python3 scripts/build_learned_candidate_dataset.py
    python3 scripts/train_learned_candidate_model.py
    python3 scripts/evaluate_learned_candidate_model.py
    python3 scripts/demo_learned_candidate_model.py

Run the v2.1 adversarial receipt:

    python3 scripts/evaluate_learned_candidate_model_adversarial.py
    python3 -m unittest discover -q

Current v2.1 boundary metrics:

- candidate_graph_contamination_count: 0
- accepted_without_typed_support_count: 0
- high_confidence_bad_block_rate: 1.0
- high_confidence_bad_total: 13
- unsupported_abstained_count: 6
- trace_schema_validity: 1.0

## Limitations

The parser is narrow and regex-based. The CIG is inspectable telemetry, not full
formal semantics. The benchmark suite is curated and toy-scope. Neural proposal
quality is not broadly claimed. Known-limit and adversarial tasks are committed
to show where the system accepts, rejects, abstains, or still needs repair.

The v2.1 result does not claim that every bad candidate receives a hard typed
rejection. Some adversarial candidates are safely blocked by abstention. The
core claim is narrower: adversarial candidates do not become proof without typed
support.

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

