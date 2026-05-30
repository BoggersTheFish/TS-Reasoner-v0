# TS-Reasoner v5.0 — Verifier-First Reasoning Firewall

v5.0 is a milestone release for the verifier-first answer arena line.

It packages v4.7, v4.8, and v4.9 into one cold-reader receipt.

## Core claim

Generated answers are treated as candidate data.

TS-Reasoner decomposes bounded claims, audits explanation support, rejects unsupported reasoning, and selects or abstains using typed verifier channels rather than confidence, fluency, or source identity.

## Included releases

- v4.7 — Verifier-First Answer Arena
- v4.8 — Claim Decomposer Arena
- v4.9 — Unsupported Claim Audit

## What this means

Candidate generators can propose answers.

TS-Reasoner then asks:

- what claim was made?
- does the claim match the question?
- is the claim typed-supported?
- did the explanation include extra unsupported claims?
- should the answer be accepted, rejected, or abstained?

## Boundary

v5.0 does not claim:

- broad NLP
- general theorem proving
- external benchmark victory
- live TensionLM runtime integration
- generated text as proof
- model confidence as proof
- candidate source identity as proof

The proof authority remains typed verifier support.

## Expected headline receipt

Generated artifact:

```text
artifacts/v5_0_reasoning_firewall_receipt.json

Expected gates:

all input reports present
all input gates passed
arena selection accuracy is 1.0 across included reports
unsupported-claim audit stress is present
wrong accepts: 0
accepted without typed support: 0
accepted with unsupported claims: 0
candidate graph contamination: 0
all gates passed: true
