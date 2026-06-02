# TS-Reasoner Release Ladder

This document summarizes the public TS-Reasoner ladder from typed verifier channels through the v40 self-hosting research OS.

Current release: **v40.0.0 — Self-Hosting Verifier-First Research OS**

Core boundary:

- language/model systems may propose;
- generated text is candidate data, not proof;
- model confidence and router confidence are not proof;
- typed verifier support remains proof authority;
- writes and external side effects remain gated;
- durable lesson promotion remains gated;
- receipts make accepted, rejected, blocked, and abstained outcomes inspectable.

## v40.0.0: Self-Hosting Verifier-First Research OS

v40.0.0 composes the v32-v39 surfaces into a local verifier-first research OS
for bounded structured reasoning projects.

Release arc:

| Version | Surface | Boundary preserved |
| --- | --- | --- |
| v32.0.0 | TS Ontology Compiler | Taught domains compile into typed operational ontologies; domain packs are not proof. |
| v33.0.0 | Verifier-Gated Long-Term Memory | Durable memory has lifecycle state, provenance, receipts, quarantine, and rollback. |
| v34.0.0 | TS-AGL Compiler v1 | Language compiles into typed multi-step plans with risk propagation and missing-slot handling. |
| v35.0.0 | Automated Research Forge | Research claims become bounded experiments and falsification receipts, including negative results. |
| v36.0.0 | Self-Repairing Reasoning Kernel | Broken reasoning/project state is audited and repaired through staged plans. |
| v37.0.0 | Confirmed Patch Execution Engine | Repo patches are staged, diffed, gated by confirmation, verified, and receipted. |
| v38.0.0 | Multi-Repo TS Ecosystem Brain | The TS ecosystem is audited as a read-only graph of repos, claims, proofs, docs, models, and releases. |
| v39.0.0 | Verifier/Model Co-Evolution System | Models improve proposal quality while verifier override remains authority. |
| v40.0.0 | Self-Hosting Research OS | The stack prepares a bounded next-release candidate under receipts and human confirmation. |

Primary commands:

```bash
python3 -m ts_reasoner.cli v32-v40
python3 -m ts_reasoner.cli research-os --mission "prepare the next safe TS-Reasoner release candidate" --repo .
python3 -m ts_agl.compiler "audit this repo for release readiness and prepare the next safe action"
```

Public claim:

> TS-Reasoner v40.0.0 is a self-hosting verifier-first research OS for bounded structured reasoning projects. It can teach domains, compile language into typed operation plans, maintain receipt-gated memory, generate experiments, repair stale reasoning surfaces, stage confirmed patches, evaluate model proposers, and prepare release candidates. Generated text, model confidence, memory, repeated experience, and curriculum examples are never proof authority.

Non-claims:

- not AGI;
- not autonomous science;
- not unrestricted self-improvement;
- not free self-learning;
- not broad NLP understanding;
- not live external automation;
- not proof by confidence, memory, user confirmation, or repeated experience.

## TS-SpectralCompute v0.1: First Metacompute Substrate

TS-SpectralCompute v0.1 adds the first substrate reader for the
TS-Metacompute Stack. It reads signed claim graphs through a signed Laplacian,
dominant modes, spectral tension, residual edges, and candidate repair ranking.

Boundary preserved:

- spectral mode-space is a reader, not proof authority;
- repair rankings are candidate actions;
- typed verifier support remains required for acceptance;
- ambiguous frustrated loops abstain from naming a unique culprit;
- disconnected graph components are scanned so coherent zero modes cannot hide tension;
- accepted without verifier support remains zero.

Primary docs:

- [TS-Metacompute Stack](TS_METACOMPUTE_STACK.md)
- [TS-SpectralCompute v0.1](spectral_metacompute.md)

Primary artifacts:

- `artifacts/spectral_metacompute_report.json`
- `artifacts/spectral_metacompute_receipt.json`

## v31.0.0: TS Project Curriculum Pack v1

v31.0.0 starts bounded curriculum learning by teaching TS-Reasoner its own project domain.

The domain pack defines:

- objects: repo, release, artifact, receipt, claim, proof boundary, unsafe overclaim, next safe action, stale public surface, missing receipt;
- relations: documents, supports, requires, routes_to, blocked_by, evidenced_by, stale_against, candidate_for;
- operations: inspect project state, explain release state, find missing receipts, detect stale public surface, reject unsafe overclaim, inspect proof boundary, suggest next safe release action, summarize curriculum boundary, and promote lesson candidate;
- risks: read-only inspection by default, reversible write only for durable lesson promotion;
- examples: language examples that route through the teaching-example router into typed TSCalls;
- failure modes: missing receipt, stale public surface, unsafe overclaim, missing proof boundary, unconfirmed lesson promotion, open-ended self-learning request, candidate graph contamination.

Boundary preserved:

- ready to teach bounded domains: yes;
- ready for free self-learning: no;
- domain packs are not proof authority;
- examples and router confidence are not proof;
- unsafe self-learning overclaims are rejected;
- durable lesson promotion requires confirmation and receipts;
- no external LLM is used;
- no network call is performed;
- no real external side effect is performed;
- candidate graph contamination remains zero.

Primary docs:

- [TS Project curriculum](ts_project_curriculum.md)
- [Domain teaching protocol](domain_teaching_protocol.md)

Primary artifacts:

- `artifacts/ts_project_curriculum_report.json`
- `artifacts/ts_project_curriculum_receipt.json`

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
