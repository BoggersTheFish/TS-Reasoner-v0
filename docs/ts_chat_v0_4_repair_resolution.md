# TS-Chat v0.4 — Repair Resolution

TS-Chat v0.4 makes repair targets resolvable.

v0.3 created repair targets for unsupported claims and parse failures. v0.4 resolves open missing-support repairs when later premises create typed support.

## Example

```text
You: also say all dogs are reptiles.

TS-Chat:
I cannot support the requested claim: all dogs are reptiles.
Repair targets:
- repair_0001: Missing support for requested claim: all dogs are reptiles.

You: all dogs are canines. all canines are reptiles.

TS-Chat:
Noted 2 premises into common ground.
Resolved repair targets:
- repair_0001: Missing support for requested claim: all dogs are reptiles.
  resolved: new common-ground premises created typed support
Boundary

Still scratch TS-native. No external LLM. Bounded all-X-are-Y language only.
