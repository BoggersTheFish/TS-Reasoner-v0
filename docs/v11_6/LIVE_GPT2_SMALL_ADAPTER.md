# TS-Reasoner v11.6.0: Live GPT-2-small Adapter

v11.6.0 adds an optional live GPT-2-small adapter for verifier-first boundary comparison.

The repo remains lightweight by default. Live GPT-2-small execution is opt-in:

```bash
pip install transformers torch
TS_REASONER_RUN_LIVE_GPT2=1 python3 scripts/v11_6/evaluate_live_gpt2_small_adapter.py

Without those optional dependencies, the evaluator still checks the adapter contract and TS-Reasoner verifier safety gates.

Boundary

This is not a broad GPT-2 replacement claim.

This release adds an adapter for controlled verifier-first comparison. GPT-2 output remains candidate text. It is not proof. The typed verifier remains proof authority.
