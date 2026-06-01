# TS-Reasoner-v0

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Runtime](https://img.shields.io/badge/runtime-stdlib_only-brightgreen)](requirements.txt)
[![CI](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml/badge.svg)](https://github.com/BoggersTheFish/TS-Reasoner-v0/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Release](https://img.shields.io/badge/release-v21.0.0-gold)](https://github.com/BoggersTheFish/TS-Reasoner-v0/releases/tag/v21.0.0)

**TS-Reasoner is a verifier-first reasoning system.**

Core line:

> Language/model systems may propose. TS verifies. Confidence is not proof. Typed verifier support is the proof boundary.

TS-Reasoner separates:

```text
candidate generation
→ candidate/proposer ranking
→ typed verifier channels
→ accept / reject / abstain
→ trace + receipt

The current milestone is:

v12.0.0 — Verifier-Gated Proposer Stack

It packages the v11 line into one bounded end-to-end system:

paragraph input
→ bounded paragraph decomposition
→ trained proposer prediction
→ typed verifier gate
→ final yes/no/abstain answer
→ trace + receipt

A trained proposer can suggest an answer, status, and support channel. That suggestion is not proof. A proposed yes only survives when the typed verifier accepts the decomposed claim with support.

Current release

Current release: v21.0.0 — TS-AGL Local Project Operator


The v21.0 release adds a bounded local project operator: TS-AGL inspects repo/docs state, uses the router stack for next-safe-action routing, stages a safe artifact write, blocks unconfirmed mutation, executes only after confirmation, and emits a project-operator receipt.

Release assets:

ts_agl_local_project_operator_report.json
ts_agl_local_project_operator_receipt.json
ts_agl_project_operator_note.json
ts_agl_router_stack_arena_report.json
ts_agl_router_stack_arena_receipt.json
ts_agl_tiny_router_model.json
ts_agl_tiny_router_train_report.json
ts_agl_tiny_router_report.json
ts_agl_tiny_router_receipt.json
ts_agl_router_dataset.jsonl
ts_agl_router_dataset_build_report.json
ts_agl_router_dataset_report.json
ts_agl_router_dataset_receipt.json
ts_agl_domain_pack_generator_report.json
ts_agl_domain_pack_generator_receipt.json
research_notes.json
ts_agl_external_side_effect_staging_report.json
ts_agl_external_side_effect_staging_receipt.json
ts_agl_interactive_workflow_ledger_report.json
ts_agl_interactive_workflow_ledger_receipt.json
ts_agl_interactive_workflow_marker.json
ts_agl_safe_write_arena_report.json
ts_agl_safe_write_arena_receipt.json
ts_agl_safe_write_marker.json
ts_agl_cross_domain_arena_report.json
ts_agl_cross_domain_arena_receipt.json
ts_agl_example_router_report.json
ts_agl_domain_pack_validation_report.json
ts_agl_routing_report.json
ts_agl_demo_receipt.json

The v12.0 receipt checks the full stack:

paragraph decomposition succeeds
trained proposer predictions are recorded
typed verifier gating produces final answers
final wrong accepts remain zero
accepted without typed support remains zero
candidate graph contamination remains zero
What this is

TS-Reasoner is:

a bounded verifier-first reasoning artifact
a typed proof-support and rejection system
a trace-producing accept/reject/abstain runtime
a safe bridge for learned or language-model candidate proposers
a receipt-first research surface for verifier-first reasoning
a small-stack testbed for keeping candidate generation separate from proof authority

The core architectural point is simple:

generated text != proof
model confidence != proof
candidate generation != proof
typed verifier support = proof boundary
What this is not

TS-Reasoner is not:

a chatbot
a broad natural-language understanding system
a general theorem prover
a GPT-2 replacement
an external benchmark victory claim
a claim that model confidence proves anything
a system where the trained proposer has proof authority

The trained proposer is deliberately subordinate to the verifier.

Why this matters

Language models often collapse three different things into one surface:

fluent generation
confidence
truth/proof

TS-Reasoner keeps them separate.

A model may produce a candidate claim. A model may assign confidence. A proposer may predict yes. None of that is proof.

Only typed verifier support can accept a claim.

That gives the system a hard safety shape:

bad proposal → verifier rejects or abstains
unsupported proposal → verifier abstains
contradictory proposal → verifier rejects
supported proposal → verifier accepts with trace
Quick start

Run the main v12 stack receipt:

python3 scripts/v12_0/evaluate_verifier_gated_stack.py

Run the full test suite:

python3 -m unittest discover -q

Run the v11/v12 path in order:

python3 scripts/v11_0/evaluate_gpt2_boundary_arena.py
python3 scripts/v11_1/evaluate_claim_normalizer.py
python3 scripts/v11_2/evaluate_relation_phrase_parser.py
python3 scripts/v11_3/evaluate_paragraph_decomposer.py
python3 scripts/v11_4/evaluate_procedural_curriculum.py
python3 scripts/v11_5/evaluate_adversarial_claim_fuzzer.py
python3 scripts/v11_6/evaluate_live_gpt2_small_adapter.py
python3 scripts/v11_7/evaluate_trace_training_dataset.py
python3 scripts/v11_8/evaluate_ts_proposer_mini.py
python3 scripts/v11_9/evaluate_neural_ts_proposer_tiny.py
python3 scripts/v12_0/evaluate_verifier_gated_stack.py
python3 -m unittest discover -q

Optional live GPT-2-small comparison:

pip install transformers torch
TS_REASONER_RUN_LIVE_GPT2=1 python3 scripts/v11_6/evaluate_live_gpt2_small_adapter.py

The default repo remains stdlib-first and CI-safe. Live GPT-2 is opt-in.

v12.0 system flow

The v12 stack is implemented in:

ts_reasoner/proposer_stack.py
scripts/v12_0/evaluate_verifier_gated_stack.py
docs/v12_0/VERIFIER_GATED_PROPOSER_STACK.md
artifacts/v12_0/verifier_gated_stack_report.json
artifacts/v12_0/verifier_gated_stack_receipt.json

Runtime flow:

1. Paragraph arrives.
2. Paragraph decomposer extracts canonical premises and candidate claim.
3. Trained proposer predicts candidate answer/status/channel.
4. Typed verifier independently checks the candidate claim.
5. Final answer is produced from verifier status, not proposer confidence.
6. Trace and receipt are written.

Example shape:

Input:
Generated text counts as candidate data.
Candidate data is not proof.
Is generated text proof?

Proposer:
candidate answer/status/channel prediction

Verifier:
abstained / unsupported_claim

Final:
abstain

The proposer can be useful without becoming authority.

Main modules

Core verifier/runtime:

ts_reasoner/support_path_verifier.py
ts_reasoner/typed_support.py
ts_reasoner/claim_normalizer.py
ts_reasoner/relation_phrase_parser.py
ts_reasoner/paragraph_decomposer.py
ts_reasoner/proposer_stack.py

Benchmark/curriculum layer:

benchmarks/gpt2_boundary/procedural_curriculum.py
benchmarks/gpt2_boundary/adversarial_fuzzer.py
benchmarks/gpt2_boundary/live_gpt2_adapter.py

Training/proposer layer:

training/v11_7/build_trace_training_data.py
training/v11_8/ts_proposer_mini.py
training/v11_9/neural_ts_proposer_tiny.py

Release authority:

release_authority.json
scripts/v8_0/check_release_authority_sync.py
docs/v11_0/GPT2_BOUNDARY_ARENA.md
Release ladder
Version	Core addition	Boundary preserved
v1.x	typed tension channels and early TensionLM candidate bridge	model output remains candidate data
v2.x	learned candidate models and verifier-trace training	learned models remain advisory
v3.x	verifier-guided candidate model and public surface hardening	typed verifier remains proof authority
v4.x	natural-language reasoning shell and GPT-2-shaped candidate fixtures	generated text remains candidate data
v5.0	verifier-first reasoning firewall	confidence/generated text/candidate source are not proof
v5.1-v5.9	TS-Chat scratch loop, repair suggestions, improvement ledger	repair suggestions are candidates, not proof
v6.0-v6.9	persistent memory, explanation traces, provenance, knowledge packs, long-run repair stress	common ground is provenance-aware; candidates do not contaminate proof graph
v7.0	self-improving verifier-first chat milestone	repair loop remains verifier-gated
v8.0	release authority and public-claim audit	public claims require receipts
v9.x	bounded candidate/proof infrastructure expansion	verifier remains authority
v10.x	GPT-2 boundary preparation	comparison remains controlled and verifier-first
v11.0	GPT-2 Boundary Arena	TS-Reasoner beats a controlled GPT-2 boundary fixture only inside the bounded arena
v11.1	Natural Claim Surface Normalization	natural surfaces normalize before typed verification
v11.2	Relation Phrase Parser	relation phrases become canonical verifier forms
v11.3	Paragraph Claim Decomposer	bounded paragraphs decompose into verifier premises and target claims
v11.4	Procedural Reasoning Curriculum	deterministic generated tasks reduce hand-built benchmark dependence
v11.5	Adversarial Claim Fuzzer	hostile mutations preserve zero wrong accepts
v11.6	Live GPT-2-small Adapter	optional live GPT-2 output remains candidate text
v11.7	Verifier Trace Training Dataset	labels replay through typed verifier traces
v11.8	TS-Proposer-Mini Baseline	trained proposer output is verifier-gated
v11.9	Neural TS-Proposer Tiny	neural proposer predictions remain non-proof
v12.0	Verifier-Gated Proposer Stack	end-to-end stack produces final answers only through verifier gate
Evidence artifacts

Important current release artifacts:

artifacts/v12_0/verifier_gated_stack_cases.jsonl
artifacts/v12_0/verifier_gated_stack_trace.jsonl
artifacts/v12_0/verifier_gated_stack_report.json
artifacts/v12_0/verifier_gated_stack_receipt.json

Important v11 substrate artifacts:

artifacts/v11_4/procedural_curriculum.jsonl
artifacts/v11_5/adversarial_fuzzer_cases.jsonl
artifacts/v11_7/verifier_trace_train.jsonl
artifacts/v11_7/verifier_trace_valid.jsonl
artifacts/v11_7/verifier_trace_test.jsonl
artifacts/v11_8/ts_proposer_mini_model.json
artifacts/v11_9/neural_ts_proposer_tiny_model.json

The artifact policy is receipt-first: claims should point to reports/receipts, not vibes.

Claim boundary

The strongest safe public claim right now:

TS-Reasoner v12.0 runs a bounded verifier-gated proposer stack end-to-end: paragraph input is decomposed, a trained proposer predicts candidate labels, the typed verifier independently gates the candidate claim, and the final answer is traceable with zero wrong accepts in the controlled arena.

Do not overclaim this as:

broad AGI
broad NLP
GPT-2 replacement
general theorem proving
external benchmark victory
proof by model confidence
proof by generated text

The point is the architecture:

proposal is useful
verification is authoritative
receipts make the boundary inspectable
One-command baseline

Classic inference entrypoint:

python3 inference.py --question "If all A are B and all B are C, are all A C?"

Current v12 stack receipt:

python3 scripts/v12_0/evaluate_verifier_gated_stack.py

Full verification:

python3 -m unittest discover -q
License

MIT.
