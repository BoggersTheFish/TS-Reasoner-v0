# TS-Chat Repair Suggestions

v5.7.0 adds bounded repair suggestions for TS-Chat repair curriculum entries.

This is the next step after v5.6 repair curriculum.

The loop is:

```text
failure → curriculum entry → repair suggestion → confirmation/verifier support
What it does

TS-Chat can read repair curriculum entries and produce inspectable repair suggestions.

Examples:

Parse failure:
sparks kinda lantern-vibe sideways??

Repair suggestion:
Did you mean: All sparks are lantern?
Missing support:
All sparks are lanterns

Repair suggestion:
Provide typed premises that support: All sparks are lanterns
Boundary

Repair suggestions are not proof.

Suggestions are not automatically accepted.

Generated language is candidate text only.

Typed verifier support or user confirmation is required before a suggestion can become accepted.

This release does not claim:

general English understanding
broad NLP
neural training
live TensionLM integration
external benchmark victory
Demo
python3 scripts/demo_ts_chat_repair_suggestions.py

Writes:

data/ts_chat_repair_suggestions_v0_7.jsonl
artifacts/ts_chat_v0_7_repair_suggestions_demo_receipt.json
Evaluation
python3 scripts/evaluate_ts_chat_repair_suggestions.py

Writes:

artifacts/ts_chat_v0_7_repair_suggestions_eval_report.json

Required gates:

repair suggestions exist
parse repair suggestions exist
missing-support repair suggestions exist
source turn links are preserved
repair target links are preserved
curriculum entry links are preserved
all suggestions remain suggested_not_accepted
accepted without confirmation count is zero
candidate graph contamination count is zero
