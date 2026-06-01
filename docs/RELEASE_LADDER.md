# TS-Reasoner Release Ladder

This document summarizes the public TS-Reasoner ladder from typed verifier channels through the v30 verifier-first local agent OS.

Current release: **v30.0.0 — Verifier-First Local Agent OS**

Core boundary:

- language/model systems may propose;
- generated text is candidate data, not proof;
- model confidence and router confidence are not proof;
- typed verifier support remains proof authority;
- writes and external side effects remain gated;
- receipts make accepted, rejected, blocked, and abstained outcomes inspectable.

## v30.0.0: Verifier-First Local Agent OS

v30.0.0 composes the v26-v29 surfaces into one bounded local operating loop:

- native conversational shell loop;
- generated evidence dashboard;
- visible proof object examples;
- one-command first-contact demo;
- composed verifier-first local agent OS runner.

Result:

- unsafe ambiguity abstains;
- destructive requests are blocked by safe abstention;
- external side-effect requests require slots and confirmation;
- unconfirmed writes are blocked;
- no external LLM is used;
- no network call is performed;
- no real external side effect is performed;
- candidate graph contamination remains zero.

Primary docs:

- [First contact](first_contact.md)
- [TS-OS conversational shell loop](ts_os_conversational_shell_loop.md)
- [Evidence dashboard](evidence_dashboard.md)
- [Proof objects](proof_objects.md)
- [Verifier-first local agent OS](verifier_first_local_agent_os.md)

Primary artifacts:

- `artifacts/ts_os_v30_report.json`
- `artifacts/ts_os_v30_receipt.json`
- `artifacts/ts_evidence_dashboard.json`
- `artifacts/proof_object_examples.json`

## v26.0.0-v29.0.0: v30 Ladder Components

These releases are internal ladder components of the v30 flagship surface:

| Version | Surface | Purpose |
| --- | --- | --- |
| v26.0.0 | Conversational shell loop | Natural-language turns route through typed TS-AGL calls and receipts. |
| v27.0.0 | Evidence dashboard | Safety and receipt metrics aggregate into one generated JSON artifact. |
| v28.0.0 | Proof object explorer | Typed verifier support becomes visible through examples. |
| v29.0.0 | First-contact demo | Outsiders can evaluate the boundary with one command. |

## v25.0.0: TS-OS v1

v25.0.0 packages the TS-AGL stack into TS-OS v1: a bounded operating layer over shell, sessions, router stack, local project operation, external adapter gating, and receipts.

Boundary preserved:

- TS-OS v1 is not broad autonomous agency;
- no external LLM is used;
- no accidental network call is performed;
- no real external side effect is performed;
- language and router confidence are not proof authority;
- candidate graph contamination remains zero.

## v20.0.0-v24.0.0: TS-AGL Operation Surfaces

This band turns TS-AGL from verifier/routing internals into bounded local operation surfaces.

| Version | Surface | Boundary preserved |
| --- | --- | --- |
| v20.0.0 | Router stack arena | Routing can choose or abstain; confidence is not proof. |
| v21.0.0 | Local project operator | Local writes are staged, gated, confirmed, and receipted. |
| v22.0.0 | Shell surface | Shell commands expose routing/operator behavior without granting proof authority. |
| v23.0.0 | Persistent session ledger | Session replay is useful state, not proof authority. |
| v24.0.0 | Controlled external adapter gate | External adapter authorization is not network execution. |

## v12.0.0-v12.1.0: Verifier-Gated Proposer Stack and Domain Routing

v12.0.0 remains the core proof-authority substrate. Paragraph input is decomposed into canonical premises and candidate claims, a proposer predicts candidate answer/status/channel, and the typed verifier independently decides the final answer.

v12.1.0 adds the TS-AGL domain example router, where domain-pack language examples teach routing behavior while unknown or low-confidence input safely abstains.

Boundary preserved:

- generated text is candidate data;
- proposer output is not proof authority;
- typed verifier status decides the final answer;
- accepted without typed support remains zero;
- candidate graph contamination remains zero.

## v11.0.0-v11.9.0: GPT-2 Boundary and Proposer Preparation

This band builds the controlled GPT-2 boundary fixture and the typed surfaces needed before the v12 verifier-gated stack:

- GPT-2 boundary arena;
- natural claim normalization;
- relation phrase parser;
- paragraph decomposer;
- procedural curriculum;
- adversarial claim fuzzer;
- optional live GPT-2-small adapter;
- verifier trace training dataset;
- TS-Proposer-Mini baseline;
- Neural TS-Proposer Tiny baseline.

Boundary preserved:

- GPT/model output remains candidate text;
- labels replay through typed verifier traces;
- neural proposer predictions remain non-proof;
- optional live GPT-2 is opt-in and not part of default CI.

## v9.0.0-v10.9.0: Runtime Kernel and Verifier-First Reasoning OS

This band packages replay, runtime policy contracts, append-only ledger, tamper-evident hash chain, checkpoint/restore, recovery drill, and receipt output into bounded runtime surfaces.

Boundary preserved:

- runtime integrity is not claim truth;
- generated text is not proof;
- candidate generation is not proof;
- model confidence is not proof;
- typed verifier support remains proof authority.

## v8.0.0-v8.9.0: Release Authority and Repair Infrastructure

This band adds public-claim audit, contradiction repair policy, missing bridge synthesis, provenance-weighted repair, branching worlds, knowledge-pack contracts, reasoning diff patches, audit cockpit, adversarial state fuzzing, and immune-system stress.

Boundary preserved:

- public claims require receipts;
- repairs are proposed and checked, not assumed;
- provenance affects repair decisions without replacing typed support.

## v5.0.0-v7.0.0: Verifier-First Chat and Repair Loops

This band introduces the verifier-first reasoning firewall, TS-Chat scratch loop, repair suggestions, improvement ledger, persistent memory, explanation traces, provenance, knowledge packs, long-run repair stress, and self-improving verifier-first chat milestone.

Boundary preserved:

- repair suggestions are candidates, not proof;
- common ground is provenance-aware;
- candidates do not contaminate the proof graph.

## v1.0.0-v4.9.0: Typed Channels, Candidate Models, and Natural-Language Shell

The early ladder builds the typed support substrate and candidate boundary:

- typed tension channels;
- TensionLM candidate bridge;
- learned candidate model;
- adversarial candidate stress;
- natural-language claim ingestion;
- benchmark harness;
- verifier-trace training data;
- training-loop smoke;
- active-learning loop;
- public surface hardening;
- GPT-2-shaped candidate fixtures;
- natural-language reasoning shell.

Boundary preserved:

- model output remains candidate data;
- learned models remain advisory;
- typed verifier support remains proof authority;
- generated text remains candidate data.

## Artifact Policy

The artifact policy is receipt-first: claims should point to reports/receipts, not vibes.

Current v30 release artifacts:

- `artifacts/ts_os_v30_report.json`
- `artifacts/ts_os_v30_receipt.json`
- `artifacts/ts_evidence_dashboard.json`
- `artifacts/proof_object_examples.json`
- `artifacts/first_contact_demo_report.json`
- `artifacts/first_contact_demo_receipt.json`
- `artifacts/first_contact_surface_report.json`
- `artifacts/ts_os_chat_loop_report.json`
- `artifacts/ts_os_chat_loop_receipt.json`
- `artifacts/ts_os_chat_loop_demo.json`

Core v12 proof-substrate artifacts:

- `artifacts/v12_0/verifier_gated_stack_cases.jsonl`
- `artifacts/v12_0/verifier_gated_stack_trace.jsonl`
- `artifacts/v12_0/verifier_gated_stack_report.json`
- `artifacts/v12_0/verifier_gated_stack_receipt.json`
