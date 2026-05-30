# TS-Chat v0.2 — Common Ground Manager

TS-Chat v0.2 upgrades the scratch TS-native chat loop with a common-ground manager.

Instead of flattening conversation into anonymous graph edges, TS-Chat now records user assertions, questions, rejected requested claims, discourse markers, support paths, and turn provenance as claim records.

## Commands

Interactive chat:

```bash
python3 -m ts_reasoner.ts_chat

or:

python3 -m ts_reasoner.cli chat

Deterministic demo:

python3 scripts/ts_chat_v0_2/run_ts_chat_common_ground_demo.py
New chat commands
what do we know?
why?
what is unsupported?
/graph
/clear
Example
You: all dogs are mammals. all mammals are animals. are all dogs animals?

TS-Chat:
Noted 2 premises into common ground.
Yes — all dogs are animals.
Verifier: accepted from common-ground support.

You: why?

TS-Chat:
all dogs are animals is supported by:
- all dogs are mammals
- all mammals are animals
Boundary

This is still bounded all-X-are-Y language.

It is not broad NLP and uses no external LLM.

The goal is to model natural-language conversation as common-ground updates that can be inspected, verified, repaired, and eventually used as training signal.
