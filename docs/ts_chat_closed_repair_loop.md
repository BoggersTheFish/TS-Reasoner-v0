# TS-Chat Closed Repair Loop

v6.0.0 is the first TS-Chat closed-loop milestone.

It runs the bounded repair pipeline end-to-end:

```text
replay repair curriculum
→ generate/read repair suggestions
→ confirm suggestions into verifier candidates
→ apply verifier outcomes
→ update before/after improvement metrics
Why this is bigger than v5.x

v5.6 created repair curriculum entries.

v5.7 created repair suggestions.

v5.8 confirmed suggestions into verifier candidates.

v5.9 measured the repair loop.

v6.0 closes the loop and reports before/after improvement.

Headline metrics

The v6.0 receipt reports:

initial open repairs
final open repairs
repairs closed this run
accepted candidates with verifier support
rejected candidates without contamination
ledger updated
zero candidate graph contamination
improvement detected
Boundary

This release does not claim:

general English understanding
broad NLP
neural training
live TensionLM integration
external benchmark victory

Generated text is not proof.

User confirmation is not proof.

Typed verifier support remains proof authority.

Demo
python3 scripts/demo_ts_chat_closed_repair_loop.py

Writes:

artifacts/ts_chat_v1_0_closed_repair_loop_receipt.json
artifacts/ts_chat_v1_0_closed_repair_loop_eval_report.json
Evaluation
python3 scripts/evaluate_ts_chat_closed_repair_loop.py

Required gates:

case count is nonzero
final open repairs are not greater than initial open repairs
at least one candidate is accepted with verifier support
at least one candidate is rejected without contamination
ledger updated is true
zero candidate graph contamination is true
improvement detected is true
Release claim

TS-Chat can replay bounded failures, apply the repair suggestion/confirmation/verifier pipeline, and produce a before/after improvement receipt while preserving the verifier-first boundary.
