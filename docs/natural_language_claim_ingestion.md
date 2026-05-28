# v2.4.0: Natural Language Claim Ingestion

TS-Reasoner v2.4 adds a bounded natural-language claim ingestion layer.

The goal is not general natural-language understanding. The goal is a narrow and inspectable bridge:

```text
bounded natural-language prompt
→ canonical relation-shaped premises
→ candidate graph claim
→ existing candidate bridge
→ typed TS-Reasoner verifier channels
→ accept / reject / abstain receipt
Supported surface

The parser supports small syllogistic and relation-shaped prompts such as:

All dogs are mammals. All mammals are animals. Are all dogs animals?
Every raven belongs to bird. Each bird falls under animal. Can we conclude all raven are animal?
All payroll_files are encrypted_messages. All encrypted_messages are sensitive_records. Does it follow that all payroll_files are sensitive_records?

The supported concept surface is intentionally simple: single-token, underscore, or hyphenated concept names.

Boundary

The parser extracts candidate data. It does not prove claims.

Proof authority remains with the existing TS-Reasoner typed channels. A parsed candidate can still be accepted, rejected, or abstained after verification.

This release does not:

load TensionLM;
train a neural model;
claim broad NLP;
allow model/parser confidence to become proof authority;
add parsed candidates directly into the premise graph.
Evaluation

The v2.4 evaluator is:

python3 scripts/evaluate_natural_language_claim_ingestion.py

It writes:

artifacts/natural_language_claim_ingestion_report.json
artifacts/natural_language_claim_ingestion_receipt.json

The release gates are:

parse expectation rate >= 0.95
malformed input safe-abstain rate = 1.0
accepted-without-typed-support count = 0
candidate graph contamination count = 0
trace schema validity = 1.0
