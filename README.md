# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v40.0.0-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v40.0.0)

**TS-Reasoner is a verifier-first operation firewall and TS-OS research stack.**

Language, models, memory, metacompute substrates, and field simulators may
propose. Typed verifier support, risk gates, confirmations, and receipts decide
what is accepted or executed.

Core line:

```text
Substrates expose tension. Models propose. TS verifies.
Confidence is not proof. Typed verifier support is the proof boundary.
```

## Current System

The current public system is the v40 self-hosting verifier-first research OS
plus the versionless **TS-OS Cognitive Physics Engine** roadmap layer.

Canonical release authority remains **v12.0.0 - Verifier-Gated Proposer Stack**.
Later TS-OS layers compose around that proof-authority substrate; they do not
replace it.

The historical v40 stack provides:

- ontology/domain teaching for bounded project domains;
- TS-AGL language-to-operation compilation;
- verifier-gated memory with provenance, lifecycle state, quarantine, rollback,
  and receipts;
- automated research forge surfaces for bounded experiments and falsification
  cases;
- self-repair audit and confirmed local patch staging;
- multi-repo ecosystem audit surfaces;
- verifier/model co-evolution reports where models remain proposers;
- a self-hosting research OS receipt pack.

The Cognitive Physics Engine adds the requested long-range TS-OS substrates as
deterministic, auditable implementations:

- `Photonic_State_Ledger`: stores graph state as deterministic frequency slots.
- `ContradictionFirewall_as_interference_grating`: simulates constructive and
  destructive wave interference over support/conflict edges.
- `Retrocausal_Fuzzer`: creates late-contradiction probes.
- `Temporal_Tension_Bridge`: back-propagates late contradiction tension into
  earlier assumption probabilities through a tamper-evident event ledger.
- `Spectral_Coupling_Telepathy`: shares constraint-shape telemetry across TS-OS
  nodes without transmitting answer packets.
- `Unified_Field_Kernel`: merges candidate generation, fuzzing, and firewall
  checks behind one zero-tension verifier gate.
- `The_Lazy_Universe_Engine`: orchestrates all substrates and emits an answer
  only when a zero-tension, verifier-supported state forms.

These are simulator contracts, not claims of literal photonic hardware,
physical retrocausality, telepathy, zero-point energy, or free truth generation.

## Commands

Run the Cognitive Physics Engine receipt:

```bash
python3 scripts/evaluate_cognitive_physics_engine.py
```

Run the CLI surface:

```bash
python3 -m ts_reasoner.cli cognitive-physics \
  --question "Does A resolve to C?"
```

Run the v32-v40 research OS receipt stack:

```bash
python3 -m ts_reasoner.cli v32-v40
```

Run the v40 mission surface:

```bash
python3 -m ts_reasoner.cli research-os \
  --mission "prepare the next safe TS-Reasoner release candidate" \
  --repo .
```

Run the spectral metacompute substrate:

```bash
python3 scripts/evaluate_spectral_metacompute.py
```

Run the full test suite:

```bash
python3 -m unittest discover -q
```

## Architecture

The stack is not:

```text
User -> LLM -> answer
```

It is:

```text
user / file / code / model output
-> TS-AGL compiler
-> typed graph / common-ground state
-> metacompute substrate scheduler
-> readable substrate evolution
-> deterministic reader
-> typed verifier
-> repair / memory / receipt
-> answer or gated action
```

### TS-Core Proof Boundary

TS-Core style verifier surfaces own typed claims, support paths,
contradiction checks, abstention, repair targets, and receipts. A model output,
frequency slot, spectral mode, memory item, user confirmation, or resonance
shape is candidate evidence until the verifier accepts it.

### TS-AGL Operation Layer

TS-AGL converts language into controlled operations such as repo inspection,
common-ground queries, support checks, repair planning, and confirmed write
staging. Risk gates classify operations as read-only, reversible write,
external side effect, or blocked/destructive.

### Memory And Receipts

Memory stores lifecycle state, not truth by repetition:

```text
accepted != proposed
rejected != forgotten
unsupported != false
candidate != proof
confirmed write != confirmed truth
```

Receipts record what happened, what gates passed, what remained blocked, and
whether any candidate graph contamination or accepted-without-support event
occurred.

### Metacompute Substrates

Implemented substrates:

- **Spectral/Fourier reader**: signed graph -> signed Laplacian -> modes,
  residuals, tension, repair ranking.
- **Photonic simulation**: signed graph -> deterministic frequency ledger ->
  interference/cancellation read.
- **Temporal bridge**: late contradiction -> backward tension updates over
  assumption priors.
- **Resonance network**: solved constraint shape -> low-bandwidth telemetry
  alignment across nodes.
- **Unified field**: candidate generation/fuzzing/firewall collapsed into one
  verifier-gated resolution surface.
- **Lazy universe orchestrator**: routes all substrate reads and accepts only
  zero-tension verifier-supported outputs.

The scheduler may choose a substrate, but acceptance still requires typed
verifier support.

## Artifacts

Cognitive Physics Engine:

- `artifacts/cognitive_physics_engine_report.json`
- `artifacts/cognitive_physics_engine_receipt.json`
- `docs/cognitive_physics_engine.md`

Spectral metacompute:

- `artifacts/spectral_metacompute_report.json`
- `artifacts/spectral_metacompute_receipt.json`
- `docs/TS_METACOMPUTE_STACK.md`
- `docs/spectral_metacompute.md`

Research OS:

- `artifacts/ontology_compiler_receipt.json`
- `artifacts/verifier_gated_memory_receipt.json`
- `artifacts/ts_agl_plan_receipt.json`
- `artifacts/research_forge_receipt.json`
- `artifacts/repair_kernel_receipt.json`
- `artifacts/patch_execution_receipt.json`
- `artifacts/ecosystem_brain_receipt.json`
- `artifacts/model_coevolution_receipt.json`
- `artifacts/research_os_receipt.json`

## Safety Dashboard

Generate the current evidence dashboard:

```bash
python3 scripts/build_ts_evidence_dashboard.py
```

Core safety invariants:

| Invariant | Required result |
| --- | ---: |
| Accepted without typed support | 0 |
| Candidate graph contamination | 0 |
| External side effects by default | 0 |
| Network calls by default | 0 |
| Destructive request safe-abstention | yes |
| Unconfirmed writes blocked | yes |
| Generated text is proof | false |
| Memory is proof | false |
| User confirmation is truth authority | false |

## Non-Claims

TS-Reasoner does not claim:

```text
AGI.
Autonomous science.
Unrestricted self-improvement.
Free self-learning.
Broad NLP understanding.
Live external automation by default.
Proof by model confidence.
Proof by memory.
Proof by user confirmation.
Proof by repeated experience.
Literal photonic computation in this repo.
Physical retrocausality.
Telepathy or instant communication.
Zero-point energy.
Hallucinations physically cannot exist.
```

The strong claim is narrower and testable:

```text
TS-Reasoner is a verifier-first architecture for inspectable reasoning over
graph-structured claims, readable substrate evolution, gated operations, and
receipt-backed audits.
```
