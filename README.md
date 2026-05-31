# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v11.0.0-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v11.0.0)

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

Current release: v11.0.0, GPT-2 Boundary Arena

v11.0.0 provides a reproducible verifier-first arena comparing TS-Reasoner
against GPT-2-small on controlled reasoning tasks. GPT-2-small is treated as a
raw language proposer. TS-Reasoner wins where typed proof authority matters:
support-path recovery, contradiction rejection, unsupported-claim abstention,
and zero accepted claims without typed verifier support.

Boundary:

- This is not a broad chatbot victory.
- This is not a full language-model replacement claim.
- This is a verifier-first reasoning boundary result.
- GPT-2 generates; TS verifies.

v10.0.0 remains the unified verifier-first reasoning OS/runtime base.

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

Run the TS-OS Alpha flow:

```bash
python3 -m ts_reasoner.runtime_os_cli alpha --scenario @data/v10_5/ts_os_alpha_scenario.json
```

Run the GPT-2 boundary arena:

```bash
python3 scripts/v11_0/evaluate_gpt2_boundary_arena.py
```

Run the latest milestone receipts:

```bash
python3 scripts/v9_8/evaluate_runtime_policy_contracts.py
python3 scripts/v9_9/evaluate_runtime_recovery_drill.py
python3 scripts/v10_0/evaluate_runtime_os.py
python3 scripts/v10_5/evaluate_ts_os_alpha.py
python3 scripts/v11_0/evaluate_gpt2_boundary_arena.py
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
| v10.5.0 | TS-OS Alpha microkernel, userspace proposers, branch worlds, proof-grid receipts | Generated text, model confidence, and runtime integrity remain non-proof |
| v10.6.0 | Typed support objects | Fake support strings stop counting as proof |
| v10.7.0 | Support path verifier | Bounded premise graphs create typed verifier traces |
| v10.8.0 | GPT-2 boundary task format | The battlefield is frozen before comparison |
| v10.9.0 | GPT-2-small baseline harness | GPT-2-small is measured as an untrusted proposer |
| v11.0.0 | GPT-2 Boundary Arena | TS beats GPT-2-small on verifier-first controlled reasoning |

## Key v10 Files

- `ts_reasoner/ts_os.py`
- `ts_reasoner/runtime_os.py`
- `ts_reasoner/runtime_os_cli.py`
- `ts_reasoner/runtime_policy_contracts.py`
- `ts_reasoner/runtime_recovery_drill.py`
- `docs/v10_5/TS_OS_ALPHA.md`
- `docs/v10_0/VERIFIER_FIRST_REASONING_OS.md`
- `data/v10_5/ts_os_alpha_scenario.json`
- `data/v10_0/runtime_os_cases.jsonl`
- `scripts/v10_5/evaluate_ts_os_alpha.py`
- `scripts/v10_0/evaluate_runtime_os.py`
- `tests/test_v10_5_ts_os_alpha.py`
- `tests/test_v10_0_runtime_os.py`
- `artifacts/runtime_os_receipt.json`

## Key v11 Files

- `ts_reasoner/typed_support.py`
- `ts_reasoner/support_path_verifier.py`
- `benchmarks/gpt2_boundary/task_schema.py`
- `benchmarks/gpt2_boundary/run_gpt2_small_baseline.py`
- `benchmarks/gpt2_boundary/run_ts_reasoner_arena.py`
- `benchmarks/gpt2_boundary/compare_ts_vs_gpt2.py`
- `data/v10_8/gpt2_boundary_tasks.jsonl`
- `scripts/v11_0/evaluate_gpt2_boundary_arena.py`
- `docs/v11_0/GPT2_BOUNDARY_ARENA.md`
- `artifacts/ts_reasoner_vs_gpt2_boundary_report.json`
- `artifacts/v11_0_gpt2_boundary_arena_receipt.json`
