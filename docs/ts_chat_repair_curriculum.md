# TS-Chat Repair Curriculum

v5.6.0 adds a bounded repair-curriculum layer for TS-Chat.

The point is not to claim general English understanding. The point is to make failures durable, inspectable, replayable, and verifier-safe.

## What it does

TS-Chat repair targets can now be exported into JSONL curriculum entries.

Each entry preserves:

- source session ID
- source turn ID
- repair target ID
- repair type
- original user text
- target claim text or target parse text
- expected repair status
- verifier boundary note

## Repair types

v5.6 covers two repair target types:

- `missing_support`
- `parse_failure`

## Boundary

Curriculum entries are not proof.

Generated language is not proof.

Candidate confidence is not proof.

Typed verifier support remains proof authority.

## Demo

```bash
python3 scripts/demo_ts_chat_repair_curriculum.py

Writes:

data/ts_chat_repair_curriculum_v0_6.jsonl
artifacts/ts_chat_v0_6_repair_curriculum_demo_receipt.json
Evaluation
python3 scripts/evaluate_ts_chat_repair_curriculum.py

Writes:

artifacts/ts_chat_v0_6_repair_curriculum_eval_report.json

Required gates:

curriculum entries exist
missing-support entries exist
parse-failure entries exist
source turn links are preserved
repair target links are preserved
resolved repairs remain represented as resolved
unsupported claims do not become proof
parse failures remain repairable
candidate graph contamination is zero
