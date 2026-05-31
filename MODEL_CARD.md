# System Card: TS-Reasoner-v0

## System

TS-Reasoner is a verifier-first reasoning runtime. It accepts candidate events,
routes them through bounded runtime policies and typed verifier boundaries,
records audit receipts, and preserves the rule that candidate data is not proof.

Current release: v10.0.0.

## Intended Use

- Inspecting bounded reasoning traces.
- Testing whether candidate claims remain advisory.
- Auditing runtime event handling through replay, ledger, checkpoint, restore,
  and recovery drills.
- Producing deterministic receipt-backed release evidence.
- Evaluating typed verifier boundaries for small relation-shaped claims.

## Out-of-Scope Use

- Legal, medical, financial, safety-critical, or production decisions.
- General theorem proving.
- Broad natural-language understanding claims.
- Chatbot replacement.
- Claims that generated text is proof.
- Claims that model confidence is proof.
- Claims that candidate generation is proof.

## Architecture

The v10 runtime surface unifies:

- runtime event processing,
- explicit policy contracts,
- typed verifier boundary checks,
- ordered replay,
- append-only audit ledger,
- tamper-evident hash chain,
- checkpoint and restore,
- recovery drill,
- JSON receipts.

Learned or language-model outputs may be candidate data, but typed verifier
support remains the proof boundary.

## Current Receipts

Run the current receipts:

```bash
python3 scripts/v9_8/evaluate_runtime_policy_contracts.py
python3 scripts/v9_9/evaluate_runtime_recovery_drill.py
python3 scripts/v10_0/evaluate_runtime_os.py
python3 -m unittest discover -q
```

Current v10 boundary gates:

- runtime policy contracts available
- recovery drill available
- replay available
- tamper-evident ledger available
- checkpoint and restore available
- unified runtime session available
- candidate_graph_contamination_count: 0

## Limitations

TS-Reasoner is bounded. It is not a general theorem prover, chatbot, or broad
natural-language understanding system. Runtime integrity proves state integrity
and audit continuity; it does not prove claim truth. Claim truth still requires
typed verifier support.

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
