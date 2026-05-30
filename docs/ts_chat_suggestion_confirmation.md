# TS-Chat Suggestion Confirmation

v5.8.0 adds bounded suggestion confirmation for TS-Chat.

The loop becomes:

```text
failure → repair target → curriculum entry → repair suggestion → user-confirmed candidate → verifier accepted/rejected
What it does

Repair suggestions can be confirmed into candidate claims.

User confirmation is not proof.

A confirmed suggestion only becomes proof if typed verifier support accepts it.

States
suggested_not_accepted
→ user_confirmed_candidate
→ verifier_accepted OR verifier_rejected
Boundary

This release does not claim:

general English understanding
broad NLP
neural training
live TensionLM integration
external benchmark victory

User confirmation creates a candidate claim, not proof.

Typed verifier support remains proof authority.

Demo
python3 scripts/demo_ts_chat_suggestion_confirmation.py

Writes:

data/ts_chat_suggestion_confirmations_v0_8.jsonl
artifacts/ts_chat_v0_8_suggestion_confirmation_demo_receipt.json
Evaluation
python3 scripts/evaluate_ts_chat_suggestion_confirmation.py

Writes:

artifacts/ts_chat_v0_8_suggestion_confirmation_eval_report.json

Required gates:

confirmations exist
accepted and rejected verifier outcomes both exist
suggestion links are preserved
curriculum entry links are preserved
repair target links are preserved
user confirmation is not proof
accepted candidates require verifier support
rejected candidates are not proof
candidate graph contamination count is zero
