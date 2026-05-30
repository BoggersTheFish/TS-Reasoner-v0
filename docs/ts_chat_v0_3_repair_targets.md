# TS-Chat v0.3 — Repair Targets

TS-Chat v0.3 models failures as repair targets.

Instead of merely saying a claim is unsupported or a message cannot be parsed, TS-Chat now records explicit repair targets in common ground.

## Adds

- missing-support repair targets
- parse-failure repair targets
- `/repairs` command
- repair targets included in session receipts
- deterministic v0.3 demo receipt

## Example

```text
You: also say all dogs are reptiles.

TS-Chat:
I cannot support the requested claim: all dogs are reptiles.
Verifier: rejected; unsupported requested claim was not added to common ground.
Repair targets:
- repair_0001: Missing support for requested claim: all dogs are reptiles.
Boundary

This is still bounded all-X-are-Y language.

No external LLM is used.
