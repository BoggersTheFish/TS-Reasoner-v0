# v40.0.0 Self-Hosting Verifier-First Research OS

TS-Reasoner v40.0.0 is a local verifier-first research OS for bounded
structured reasoning projects.

It can:

- teach domains through compiled operational ontologies;
- compile natural language into typed TS-AGL operation plans;
- maintain durable memory with lifecycle state, provenance, receipts, quarantine,
  and rollback;
- generate bounded research experiments, falsification cases, reports, and
  receipts;
- audit and repair stale reasoning/project state through staged plans;
- stage and apply confirmed patches with diffs, rollback metadata, verification
  commands, and receipts;
- audit the wider TS ecosystem as a dry-run graph of repos, claims, proofs,
  docs, models, and releases;
- evaluate model proposers from verified traces without granting model
  authority;
- prepare a bounded next-release candidate under receipts and human
  confirmation.

v40 composes bounded v32-v39 surfaces into one self-hosting research OS receipt.
It does not claim each subsystem is a fully mature autonomous implementation.

## Public Claim

TS-Reasoner v40.0.0 is a self-hosting verifier-first research OS for bounded
structured reasoning projects. It can teach domains, compile language into typed
operation plans, maintain receipt-gated memory, generate experiments, repair
stale reasoning surfaces, stage confirmed patches, evaluate model proposers,
and prepare release candidates. Generated text, model confidence, memory,
repeated experience, and curriculum examples are never proof authority.

## Non-Claims

- Not AGI.
- Not autonomous science.
- Not unrestricted self-improvement.
- Not free self-learning.
- Not broad NLP understanding.
- Not live external automation.
- Not proof by confidence.
- Not proof by memory.
- Not proof by user confirmation.
- Not proof by repeated experience.

## Release Stack

| Version | Surface | Receipt |
| --- | --- | --- |
| v32.0.0 | TS Ontology Compiler | `artifacts/ontology_compiler_receipt.json` |
| v33.0.0 | Verifier-Gated Long-Term Memory | `artifacts/verifier_gated_memory_receipt.json` |
| v34.0.0 | TS-AGL Compiler v1 | `artifacts/ts_agl_plan_receipt.json` |
| v35.0.0 | Automated Research Forge | `artifacts/research_forge_receipt.json` |
| v36.0.0 | Self-Repairing Reasoning Kernel | `artifacts/repair_kernel_receipt.json` |
| v37.0.0 | Confirmed Patch Execution Engine | `artifacts/patch_execution_receipt.json` |
| v38.0.0 | Multi-Repo TS Ecosystem Brain | `artifacts/ecosystem_brain_receipt.json` |
| v39.0.0 | Verifier/Model Co-Evolution System | `artifacts/model_coevolution_receipt.json` |
| v40.0.0 | Self-Hosting Research OS | `artifacts/research_os_receipt.json` |

## Commands

Generate the complete v32-v40 receipt pack:

```bash
python3 scripts/evaluate_v32_v40_research_os.py
```

Run the v40 mission surface:

```bash
python3 -m ts_reasoner.cli research-os \
  --mission "prepare the next safe TS-Reasoner release candidate" \
  --repo .
```

Compile a typed TS-AGL plan from language:

```bash
python3 -m ts_agl.compiler \
  "audit this repo for release readiness and prepare the next safe action"
```

## Boundary

The v40 stack can stage and execute confirmed local patch writes through the
patch engine, but confirmation only authorizes bounded mutation. It does not
authorize truth. Memory persists lessons, but memory does not authorize truth.
Models propose, but models do not authorize truth.

Typed verifier support remains the proof boundary.
