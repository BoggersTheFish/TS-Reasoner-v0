# TS-Reasoner v9.3.0: Runtime Replay CLI

v9.3.0 adds a bounded CLI surface for runtime replay sessions.

The replay CLI can process a multi-event session file through the verifier-first runtime kernel.

Example:

```bash
python3 -m ts_reasoner.runtime_replay_cli replay --session @data/v9_3/runtime_replay_cli_session.json
What v9.3.0 adds
replay CLI command
session JSON input
ordered multi-event replay from terminal
safe invalid-session rejection
replay action output
final state output
receipt output
zero candidate graph contamination gate
Boundary

CLI replay is not proof.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
