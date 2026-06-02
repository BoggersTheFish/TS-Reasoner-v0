# System Card: TS-Reasoner-v0

## System

TS-Reasoner is a verifier-first research OS for bounded structured reasoning
projects. It lets language/model systems propose claims, plans, experiments,
patches, and release-candidate actions, but typed verifier support, risk gates,
confirmations, and receipts decide what is accepted or executed.

Current release: v40.0.0.

## Intended Use

- Compiling taught domains into typed operational ontologies.
- Compiling natural language into bounded multi-step TS-AGL operation plans.
- Maintaining durable lessons with verifier-gated memory state, provenance,
  receipt support, quarantine, and rollback.
- Generating bounded research experiment plans, synthetic benchmarks,
  falsification cases, reports, and receipts.
- Auditing and repairing stale reasoning/project state through staged plans.
- Staging confirmation-gated patches with diffs, rollback metadata, tests, and
  patch receipts.
- Auditing the wider TS ecosystem as a dry-run graph of repos, docs, models,
  releases, claims, and proof boundaries.
- Evaluating model proposers from verified traces while keeping models
  non-authoritative.
- Preparing a bounded next release candidate under receipts and human
  confirmation.

## Out-of-Scope Use

- AGI claims.
- Autonomous science claims.
- Unrestricted self-improvement.
- Free self-learning.
- Broad natural-language understanding claims.
- Live external automation by default.
- Legal, medical, financial, safety-critical, or production decisions.
- General theorem proving.
- Claims that generated text is proof.
- Claims that model confidence is proof.
- Claims that memory, user confirmation, repeated experience, or curriculum
  examples are proof.

## Architecture

The v40 surface composes:

- v32 TS Ontology Compiler
- v33 Verifier-Gated Long-Term Memory
- v34 TS-AGL Compiler v1
- v35 Automated Research Forge
- v36 Self-Repairing Reasoning Kernel
- v37 Confirmed Patch Execution Engine
- v38 Multi-Repo TS Ecosystem Brain
- v39 Verifier/Model Co-Evolution System
- v40 Self-Hosting Verifier-First Research OS

Generated text, learned model output, memory items, repeated examples, and user
confirmation may influence candidate structure. They do not authorize truth.
Typed verifier support remains the proof boundary.

## Current Receipts

Run the v32-v40 receipt pack:

```bash
python3 scripts/evaluate_v32_v40_research_os.py
```

Run the v40 mission surface:

```bash
python3 -m ts_reasoner.cli research-os \
  --mission "prepare the next safe TS-Reasoner release candidate" \
  --repo .
```

Run the full suite:

```bash
python3 -m unittest discover -q
```

Current v40 boundary gates:

- ontology compiler emits typed operations and hard negatives
- unsafe durable memory is quarantined
- TS-AGL plans propagate risk and confirmation requirements
- research forge emits falsification-first bounded plans
- repair kernel requires confirmation for repair actions
- patch engine blocks unconfirmed mutation
- ecosystem audit remains dry-run by default
- model proposer remains non-authoritative
- accepted_without_typed_support remains zero
- candidate_graph_contamination_count remains zero

## Limitations

TS-Reasoner is bounded. It is not AGI, autonomous science, unrestricted
self-improvement, free self-learning, broad NLP, or a production decision
system. Confirmation can authorize a bounded write; it does not authorize truth.
Memory can persist lessons; it does not authorize truth. Claim truth still
requires typed verifier support.

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
