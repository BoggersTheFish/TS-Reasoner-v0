# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v30.0.0-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v30.0.0)

**TS-Reasoner is a verifier-first operation firewall.**

It lets language/model systems propose actions or claims, but only typed verifier support, risk gates, confirmations, and receipts decide what is accepted or executed.

Core line:

> Language/model systems may propose. TS verifies. Confidence is not proof. Typed verifier support is the proof boundary.

## Current Release

Current release: **v30.0.0 — Verifier-First Local Agent OS**

TS-OS v30 packages TS-AGL into one bounded verifier-first local operating surface:

```text
language request
-> conversational shell loop
-> router stack arbitration
-> LanguageMove / TSCall
-> risk gate / confirmation gate
-> local project operator / controlled adapter gate / proof object examples
-> ResultPacket
-> evidence dashboard
-> trace + receipt
```

Language is interface/caller, not proof authority. Router confidence is not proof. Session replay is not proof. External gate authorization is not execution. Local writes remain confirmation-gated, and the v30 surface performs no accidental network call or real external side effect.

Core proof authority substrate: **v12.0.0 — Verifier-Gated Proposer Stack**.

The v12 verifier-gated proposer stack remains the proof-authority substrate; v30 makes that verifier-first boundary inspectable through local operating demos, proof objects, reports, and receipts.

## First Contact

Run the one-command public demo:

```bash
python3 scripts/demo_first_contact.py
```

Expected result:

```text
TS-Reasoner first-contact demo passed.

Safe route: PASS
Unsafe abstention: PASS
External side effect blocked: PASS
Typed proof boundary: PASS
Receipt written: PASS
```

What happens when I type X?

```text
User says: "delete everything and push it"
TS-OS routes: ts_reasoner.route_unknown
Risk: read_only
Action taken: none

User says: "what should we do next?"
TS-OS routes: git_repo.next_safe_release_action
Risk: read_only
Action taken: safe inspection/suggestion

User says: "stage an external side effect"
TS-OS routes: external_service.send_notification_dry_run
Risk: external_side_effect
Action taken: none; missing recipient/message; confirmation required
```

## Safety Dashboard

Generate the current evidence dashboard:

```bash
python3 scripts/build_ts_evidence_dashboard.py
```

Latest release safety surface:

| Metric | v30 release result |
| --- | ---: |
| Wrong accepts | 0 |
| Accepted without typed support | 0 |
| Candidate graph contamination | 0 |
| External side effects performed | 0 |
| Network calls performed | 0 |
| Destructive request safe-abstention | yes |
| Unconfirmed writes blocked | yes |
| External LLM used | false |
| All gates passed | true |

Dashboard artifact:

- `artifacts/ts_evidence_dashboard.json`

## Proof Objects

Typed proof examples are visible, not implied:

```bash
python3 scripts/show_proof_object_examples.py
```

Each proof object example shows:

- claim
- normalized claim
- support path
- typed channel
- verifier decision
- why it was accepted, rejected, or abstained
- why model confidence was ignored

Proof object artifact:

- `artifacts/proof_object_examples.json`

## Quick Start

Run the v30 local agent OS evaluation:

```bash
python3 scripts/evaluate_ts_os_v30.py
```

Run the conversational shell demo and report:

```bash
python3 scripts/run_ts_os_chat_loop_demo.py
python3 scripts/evaluate_ts_os_chat_loop.py
```

Run the full test suite:

```bash
python3 -m unittest discover -q
```

Optional live GPT-2-small comparison:

```bash
pip install transformers torch
TS_REASONER_RUN_LIVE_GPT2=1 python3 scripts/v11_6/evaluate_live_gpt2_small_adapter.py
```

The default repo remains stdlib-first and CI-safe. Live GPT-2 is opt-in.

## Release Assets

The v30 GitHub release publishes these JSON assets:

- `ts_os_chat_loop_report.json`
- `ts_os_chat_loop_receipt.json`
- `ts_os_chat_loop_demo.json`
- `ts_evidence_dashboard.json`
- `proof_object_examples.json`
- `first_contact_demo_report.json`
- `first_contact_demo_receipt.json`
- `first_contact_surface_report.json`
- `ts_os_v30_report.json`
- `ts_os_v30_receipt.json`

## Start Here

- [First contact](docs/first_contact.md)
- [TS-OS conversational shell loop](docs/ts_os_conversational_shell_loop.md)
- [Evidence dashboard](docs/evidence_dashboard.md)
- [Proof objects](docs/proof_objects.md)
- [Verifier-first local agent OS](docs/verifier_first_local_agent_os.md)
- [Release ladder](docs/RELEASE_LADDER.md)
- [Verifier-gated proposer stack](docs/v12_0/VERIFIER_GATED_PROPOSER_STACK.md)

## What This Is

TS-Reasoner is:

- a bounded verifier-first reasoning artifact
- a typed proof-support and rejection system
- a trace-producing accept/reject/abstain runtime
- a safe bridge for learned or language-model candidate proposers
- a receipt-first research surface for verifier-first reasoning
- a local operation firewall for typed, risk-classified actions

The core architectural point is simple:

```text
generated text != proof
model confidence != proof
candidate generation != proof
typed verifier support = proof boundary
```

## What This Is Not

TS-Reasoner is not:

- a chatbot
- broad autonomous agency
- a broad natural-language understanding claim
- a general theorem prover
- a GPT-2 replacement
- an external benchmark victory claim
- a system where model confidence proves anything
- a system where generated text or router confidence has proof authority

The trained proposer and router stack are deliberately subordinate to typed verifier support, risk gates, confirmations, and receipts.

## Why This Matters

Language models often collapse three different things into one surface:

- fluent generation
- confidence
- truth/proof

TS-Reasoner keeps them separate.

A model may produce a candidate claim. A model may assign confidence. A proposer may predict a route or answer. None of that is proof.

Only typed verifier support can accept a claim or authorize a typed boundary. That gives the system a hard safety shape:

```text
bad proposal -> verifier rejects or abstains
unsupported proposal -> verifier abstains
contradictory proposal -> verifier rejects
supported proposal -> verifier accepts with trace
risky operation -> gate blocks until required slots/confirmation exist
accepted operation -> receipt records the route, gate result, and action
```

## Core v12 Substrate

The v12 verifier-gated proposer stack is implemented in:

- `ts_reasoner/proposer_stack.py`
- `scripts/v12_0/evaluate_verifier_gated_stack.py`
- `docs/v12_0/VERIFIER_GATED_PROPOSER_STACK.md`
- `artifacts/v12_0/verifier_gated_stack_report.json`
- `artifacts/v12_0/verifier_gated_stack_receipt.json`

Runtime flow:

1. Paragraph arrives.
2. Paragraph decomposer extracts canonical premises and candidate claim.
3. Trained proposer predicts candidate answer/status/channel.
4. Typed verifier independently checks the candidate claim.
5. Final answer is produced from verifier status, not proposer confidence.
6. Trace and receipt are written.

Classic inference entrypoint:

```bash
python3 inference.py --question "If all A are B and all B are C, are all A C?"
```

Core v12 stack receipt:

```bash
python3 scripts/v12_0/evaluate_verifier_gated_stack.py
```

## Main Modules

Core verifier/runtime:

- `ts_reasoner/support_path_verifier.py`
- `ts_reasoner/typed_support.py`
- `ts_reasoner/claim_normalizer.py`
- `ts_reasoner/relation_phrase_parser.py`
- `ts_reasoner/paragraph_decomposer.py`
- `ts_reasoner/proposer_stack.py`

TS-OS / TS-AGL operating surface:

- `ts_agl/os/chat_loop.py`
- `ts_agl/os/evidence_dashboard.py`
- `ts_agl/os/first_contact_demo.py`
- `ts_agl/os/verifier_first_local_agent_os.py`
- `ts_agl/os/ts_os_v1.py`
- `ts_agl/external/adapter_gate.py`
- `ts_agl/arena/local_project_operator.py`

Training/proposer layer:

- `training/v11_7/build_trace_training_data.py`
- `training/v11_8/ts_proposer_mini.py`
- `training/v11_9/neural_ts_proposer_tiny.py`

Release authority:

- `release_authority.json`
- `scripts/v8_0/check_release_authority_sync.py`
- `docs/v8_0/CANONICAL_RELEASE_AUTHORITY.md`

## Release Ladder

| Version | Core addition | Boundary preserved |
| --- | --- | --- |
| v1.x | typed tension channels and early TensionLM candidate bridge | model output remains candidate data |
| v2.x | learned candidate models and verifier-trace training | learned models remain advisory |
| v3.x | verifier-guided candidate model and public surface hardening | typed verifier remains proof authority |
| v4.x | natural-language reasoning shell and GPT-2-shaped candidate fixtures | generated text remains candidate data |
| v5.x-v7.x | verifier-first chat, repair, memory, provenance, and self-improvement loops | repair suggestions are candidates, not proof |
| v8.x | release authority and public-claim audit | public claims require receipts |
| v9.x-v10.x | runtime kernel, replay, ledger, checkpoint, recovery, and policy contracts | runtime integrity is not claim truth |
| v11.x | GPT-2 boundary arena, natural claim normalization, parser/decomposer, proposer baselines | GPT/model output remains verifier-gated candidate data |
| v12.x | verifier-gated proposer stack and TS-AGL domain routing | end-to-end answers require typed verifier support |
| v20.x-v25.x | TS-AGL router stack, local project operator, shell, session ledger, external adapter gate, TS-OS v1 | local operations are risk-gated and receipted |
| v26.x-v30.x | conversational shell loop, evidence dashboard, proof objects, first-contact demo, verifier-first local agent OS | unsafe ambiguity abstains; writes/effects require confirmation; receipts explain actions |

Full ladder:

- [Release ladder](docs/RELEASE_LADDER.md)
- [Release notes](RELEASE_NOTES.md)

## Claim Boundary

The strongest safe public claim right now:

> TS-Reasoner v30.0.0 packages TS-AGL into a verifier-first local agent OS: a bounded operating layer over conversational shell routing, evidence dashboard aggregation, proof object examples, first-contact demo, local project operation, controlled external adapter gating, and receipts. Language, router confidence, session replay, and external gate authorization are not proof authority. Local writes remain confirmation-gated, no accidental network call is performed, no real external side effect is performed, and candidate graph contamination remains zero in the controlled release surface.

Do not overclaim this as:

- broad AGI
- broad autonomous agency
- broad NLP
- GPT-2 replacement
- general theorem proving
- external benchmark victory
- proof by model confidence
- proof by generated text

The point is the architecture:

```text
proposal is useful
verification is authoritative
receipts make the boundary inspectable
```

## License

MIT.
