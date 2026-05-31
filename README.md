# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v8.0.2-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v8.0.2)

TS-Reasoner is a verifier-first reasoning system.

Core line:

```text
LLMs propose.
TS verifies.
Confidence is not proof.
Typed traces show why.

It separates candidate generation, learned/advisory ranking, typed proof verification, and traceable rejection or abstention.

candidate proposer
-> learned/advisory ranking
-> typed verifier channels
-> accept / reject / abstain trace
-> receipt
Current flagship release

Current release:

https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v8.0.2

v8.0.2 adds Canonical Release Authority: a machine-readable authority file plus audit scripts, docs, tests, report, and receipt for checking whether TS-Reasoner's public/internal release surface agrees with its receipt-backed state.

It adds:

release_authority.json
docs/v8_0/CANONICAL_RELEASE_AUTHORITY.md
scripts/v8_0/audit_release_authority.py
scripts/v8_0/check_release_authority_sync.py
data/v8_0/release_authority_surface_cases.jsonl
artifacts/release_authority_audit_report.json
artifacts/release_authority_audit_receipt.json
tests/test_v8_0_release_authority.py

Previous concrete stress baseline:

v6.9.0 long-run self-repair stress report
40/40 repair cycles passed
zero candidate graph contamination
no external LLM used
generated text, repair targets, and knowledge-pack imports remain non-proof

Boundary:

candidate generation != proof
model confidence != proof
generated text != proof
typed verifier support = proof boundary
release receipts are required for public release claims
Flagship evidence

v8.0.2 Canonical Release Authority:

authority_json_valid: true
readme_current_release_matches_authority: true
docs_current_release_matches_authority: true
previous_v6_9_receipt_visible: true
public_surface_overclaim_count: 0
candidate_graph_contamination_count: 0
all_gates_passed: true

v6.9.0 long-run self-repair stress baseline:

cycles: 40
cycle_pass_rate: 1.0
failed_cycles: 0
candidate_graph_contamination_count: 0
external_llm_used: false
Run the current receipts
python3 scripts/v8_0/audit_release_authority.py
python3 scripts/v8_0/check_release_authority_sync.py
python3 -m unittest discover -q
What this is

TS-Reasoner is:

a bounded verifier-first reasoning artifact;
a typed trace system;
a candidate rejection and abstention system;
a safe bridge for learned or language-model candidate proposers;
a receipt-first research surface for verifier-first reasoning;
a release-authority system for keeping public/internal claims synced with receipt-backed state.
What this is not

TS-Reasoner is not:

a chatbot;
a general theorem prover;
a broad natural-language understanding system;
an external benchmark victory claim;
live TensionLM runtime integration;
a system where model confidence becomes proof authority.
Why this matters

Language models often entangle candidate generation, confidence, and proof.

TS-Reasoner keeps those roles separate.

A model may propose or rank a candidate claim, but the claim is not accepted unless typed verifier channels support it.

v8.0.2 extends that discipline to release truth itself.

Core boundary
candidate generation != proof
model confidence != proof
generated text != proof
typed verifier support = proof boundary
release receipts are required for public release claims
Key v8.0 files
release_authority.json
docs/v8_0/CANONICAL_RELEASE_AUTHORITY.md
scripts/v8_0/audit_release_authority.py
scripts/v8_0/check_release_authority_sync.py
data/v8_0/release_authority_surface_cases.jsonl
artifacts/release_authority_audit_report.json
artifacts/release_authority_audit_receipt.json
tests/test_v8_0_release_authority.py
Release ladder
Version	Core addition	Boundary
v1.x	typed tension channels and TensionLM candidate bridge	TensionLM output remains candidate data
v2.x	learned candidate models and verifier-trace training	learned models remain advisory
v3.x	verifier-guided candidate model and proposer boundary	typed verifier remains proof authority
v4.x	live proposer sandbox and bounded natural-language shell	generated text becomes candidate data
v5.x	verifier-first reasoning firewall and TS-Chat scratch loop	confidence and generated text remain non-proof
v6.x	persistent TS-Chat memory, repair memory, provenance, knowledge packs, and long-run stress	state survives reloads without proof contamination
v8.0	Canonical Release Authority	release truth surface is machine-audited
One-command baseline
python3 inference.py --question "If all A are B and all B are C, are all A C?"

That writes artifacts/latest_trace.json and prints the selected answer, selected chain, and global tension.
