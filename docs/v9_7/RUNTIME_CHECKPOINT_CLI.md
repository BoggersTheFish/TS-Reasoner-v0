# TS-Reasoner v9.7.0: Runtime Checkpoint CLI

v9.7.0 adds a bounded CLI surface for runtime checkpoint and restore.

Example:

```bash
python3 -m ts_reasoner.runtime_checkpoint_cli checkpoint --session @data/v9_7/checkpoint_cli_good_session.json
python3 -m ts_reasoner.runtime_checkpoint_cli restore --checkpoint @checkpoint.json
What v9.7.0 adds
checkpoint CLI command
restore CLI command
session JSON input
checkpoint JSON output
checkpoint restore output
invalid-session safe rejection
zero candidate graph contamination gate
Boundary

Checkpoint CLI output is not proof of claim truth.

Checkpoint restore proves runtime state integrity only.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
