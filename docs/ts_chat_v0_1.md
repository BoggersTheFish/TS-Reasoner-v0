# TS-Chat v0.1

TS-Chat v0.1 is the first scratch TS-native conversational loop inside TS-Reasoner.

It does not use an external LLM.

## Goal

Provide a minimal ChatGPT-like terminal interaction while keeping the internals TS-native and inspectable.

## What it supports

Bounded natural language forms:

- `all dogs are mammals`
- `all mammals are animals`
- `are all dogs animals?`
- `also say all dogs are reptiles`

## What it does

- parses bounded premises into a working relation graph
- keeps multi-turn session state
- checks questions by transitive typed support
- rejects unsupported requested claims
- composes a natural language response
- writes a session receipt

## Command

Interactive chat:

```bash
python3 -m ts_reasoner.ts_chat

Deterministic demo:

python3 scripts/ts_chat_v0_1/run_ts_chat_demo.py
Boundary

This is not a broad NLP system.

It is a scratch TS-native bounded chat loop designed to expose failures rather than hide them.

No external LLM is used.
