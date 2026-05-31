# TS-Reasoner v10.0.0: Verifier-First Reasoning OS

v10.0.0 packages the v9 runtime line into one bounded verifier-first runtime
surface.

The v10 runtime session unifies:

- ordered replay
- runtime policy contracts
- append-only audit ledger
- tamper-evident hash chain
- checkpoint and restore
- recovery drill
- receipt output

## What v10.0.0 proves

TS-Reasoner can process candidate runtime events through a single auditable
session surface while preserving the proof boundary.

Candidate data can be quarantined, opened as repair, isolated into branch
worlds, checked as knowledge-pack data, replayed, recorded, checkpointed, and
restored without mutating accepted common ground as proof.

## Boundary

v10.0.0 is not a chatbot.

v10.0.0 is not broad natural-language understanding.

v10.0.0 is not a general theorem prover.

Generated text is not proof.

Candidate generation is not proof.

Model confidence is not proof.

Typed verifier support remains the proof boundary.

## CLI

```bash
python3 -m ts_reasoner.runtime_os_cli suite --session @data/v10_0/runtime_os_session.json
python3 -m ts_reasoner.cli v10
```
