# TS-Reasoner v4.6 — Milestone CLI

TS-Reasoner v4.6 adds a command-line surface for the v4.5 milestone receipt pack.

This is a usability release, not a new reasoning capability claim.

## Command

```bash
python3 -m ts_reasoner.cli milestone

Or through the package console script:

ts-reasoner milestone
What it prints

The command prints the verifier-first milestone receipt headline:

input reports: 8
known cases: 114
known candidates: 151
wrong accepts: 0
accepted without typed support: 0
candidate graph contamination: 0
all gates passed: true
Boundary

The CLI does not change proof authority.

confidence is not proof
generated text is not proof
external benchmark text is not proof
typed verifier channels remain proof authority
