# TS-OS Conversational Shell Loop

v26.0.0 adds a native conversational shell loop over the existing TS-AGL stack.

The loop is intentionally small:

```text
user text
-> router stack proposal
-> TSCall
-> risk / missing-slot / confirmation gate
-> adapter or abstention
-> ResultPacket
-> turn receipt
```

Language proposes. The typed call and gate result decide what happens.

Run:

```bash
python3 scripts/run_ts_os_chat_loop_demo.py
python3 scripts/evaluate_ts_os_chat_loop.py
```

Artifacts:

- `artifacts/ts_os_chat_loop_demo.json`
- `artifacts/ts_os_chat_loop_report.json`
- `artifacts/ts_os_chat_loop_receipt.json`

Boundaries:

- no external LLM
- no real external side effect
- no network call
- no candidate graph contamination
- destructive ambiguity abstains
- external side effects require required slots and confirmation
- confidence is recorded but ignored as proof
