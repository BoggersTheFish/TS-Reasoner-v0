# TS-Reasoner v9.1.0: Runtime CLI

v9.1.0 adds a bounded CLI surface for the verifier-first runtime kernel.

The kernel can now be called from terminal with:

```bash
python3 -m ts_reasoner.runtime_cli process-event --event '<json>' --state '<json>'
What v9.1.0 adds
process-event CLI command
JSON event input
JSON state input
safe invalid-input rejection
kernel action output
audit output
receipt output
zero candidate graph contamination gate
Boundary

The CLI is only a runtime surface.

CLI input is not proof.

Generated text is not proof.

Candidate generation is not proof.

Typed verifier support remains the proof boundary.
