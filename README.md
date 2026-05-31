# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v10.0.0-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v10.0.0)

TS-Reasoner is a verifier-first reasoning runtime.

Core line:

```text
LLMs propose.
TS verifies.
Confidence is not proof.
Generated text is not proof.
Typed traces show why.
```

TS-Reasoner separates candidate generation, learned/advisory ranking, typed
proof verification, traceable rejection or abstention, runtime audit, and
receipt-backed release claims.

```text
candidate event
-> runtime policy contract
-> typed verifier boundary
-> quarantine / repair / branch / check
-> replay + ledger + checkpoint
-> receipt
```

## Current Release

Current release: v10.0.0, Verifier-First Reasoning OS

v10.0.0 packages the v9 runtime line into one bounded verifier-first runtime
surface:

- ordered replay
- runtime policy contracts
- append-only audit ledger
- tamper-evident hash chain
- checkpoint and restore
- recovery drill
- unified runtime session receipt

v9.8.0 added runtime policy contracts.

v9.9.0 added runtime recovery drills.

v10.0.0 unifies those pieces into the verifier-first reasoning OS surface.

## What This Is

TS-Reasoner is:

- a bounded verifier-first reasoning artifact
- a typed trace system
- a candidate rejection and abstention system
- a safe bridge for learned or language-model candidate proposers
- an auditable runtime with replay, ledger, checkpoint, restore, and recovery
- a receipt-first research surface for verifier-first reasoning

## What This Is Not

TS-Reasoner is not:

- a chatbot
- a general theorem prover
- a broad natural-language understanding system
- an external benchmark victory claim
- a system where model confidence becomes proof authority
- a system where generated text becomes proof authority

## Proof Boundary

```text
candidate generation != proof
model confidence != proof
generated text != proof
runtime integrity != claim truth
typed verifier support = proof boundary
release receipts are required for public release claims
```

## Run

Run a simple reasoner example:

```bash
python3 inference.py --question "If all A are B and all B are C, are all A C?"
```

Run the v10 unified runtime surface:

```bash
python3 -m ts_reasoner.runtime_os_cli suite --session @data/v10_0/runtime_os_session.json
python3 -m ts_reasoner.cli v10
```

Run the latest milestone receipts:

```bash
python3 scripts/v9_8/evaluate_runtime_policy_contracts.py
python3 scripts/v9_9/evaluate_runtime_recovery_drill.py
python3 scripts/v10_0/evaluate_runtime_os.py
```

Run all tests:

```bash
python3 -m unittest discover -q
```

## Release Ladder

| Version | Core addition | Boundary |
| --- | --- | --- |
| v1.x | Typed tension channels and TensionLM candidate bridge | TensionLM output remains candidate data |
| v2.x | Learned candidate models and verifier-trace training | Learned models remain advisory |
| v3.x | Verifier-guided candidate model and proposer boundary | Typed verifier remains proof authority |
| v4.x | Live proposer sandbox and bounded natural-language shell | Generated text becomes candidate data |
| v5.x | Verifier-first reasoning firewall and TS-Chat scratch loop | Confidence and generated text remain non-proof |
| v6.x | Persistent TS-Chat memory, repair memory, provenance, knowledge packs, and stress tests | State survives reloads without proof contamination |
| v8.x | Canonical release authority and immune-system runtime pieces | Public release truth is machine-audited |
| v9.x | Runtime kernel, CLI, replay, ledger, checkpoint, restore, policy contracts, recovery drill | Runtime integrity remains separate from claim truth |
| v10.0.0 | Unified verifier-first reasoning OS/runtime surface | Typed verifier support remains proof authority |

## Key v10 Files

- `ts_reasoner/runtime_os.py`
- `ts_reasoner/runtime_os_cli.py`
- `ts_reasoner/runtime_policy_contracts.py`
- `ts_reasoner/runtime_recovery_drill.py`
- `docs/v10_0/VERIFIER_FIRST_REASONING_OS.md`
- `data/v10_0/runtime_os_cases.jsonl`
- `scripts/v10_0/evaluate_runtime_os.py`
- `tests/test_v10_0_runtime_os.py`
- `artifacts/runtime_os_receipt.json`
