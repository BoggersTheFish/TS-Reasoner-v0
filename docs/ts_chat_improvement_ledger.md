# TS-Chat Improvement Ledger

v5.9.0 adds an improvement ledger for the TS-Chat repair loop.

This is the scoreboard release before v6.0.

## Loop measured

```text
repair curriculum → repair suggestions → user-confirmed candidates → verifier outcomes
What it measures

The ledger tracks:

curriculum entry count
repair suggestion count
confirmation count
confirmed candidate count
verifier accepted count
verifier rejected count
open repair count
resolved repair count
measurable loop coverage rate
accepted confirmation rate
candidate graph contamination status
Boundary

Ledger metrics are not proof of broad language understanding.

The ledger measures workflow progress through the bounded TS-Chat repair loop.

Typed verifier support remains proof authority.

This release does not claim:

general English understanding
broad NLP
neural training
live TensionLM integration
external benchmark victory
Demo
python3 scripts/demo_ts_chat_improvement_ledger.py

Writes:

artifacts/ts_chat_v0_9_improvement_ledger.json
artifacts/ts_chat_v0_9_improvement_ledger_demo_receipt.json
Evaluation
python3 scripts/evaluate_ts_chat_improvement_ledger.py

Writes:

artifacts/ts_chat_v0_9_improvement_ledger_eval_report.json

Required gates:

curriculum entries exist
repair suggestions exist
confirmations exist
accepted and rejected verifier outcomes both exist
measurable loop coverage rate is 1.0
accepted confirmation rate is between 0.0 and 1.0
candidate graph contamination is zero
v6.0 setup

v5.9 gives v6.0 a measurable target.

v6.0 should close the loop:

replay failures → suggest repairs → confirm candidates → verify → update ledger → show measurable improvement

