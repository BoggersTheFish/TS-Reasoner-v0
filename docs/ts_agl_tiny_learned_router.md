# TS-AGL Tiny Learned Router

v19.0.0 adds a tiny dependency-free learned AGL router.

It trains on the v18 trace-mined router dataset:

```text
artifacts/ts_agl_router_dataset.jsonl

The model is a small multinomial Naive Bayes router over token counts.

Commands
python3 scripts/train_ts_agl_tiny_router.py
python3 scripts/evaluate_ts_agl_tiny_router.py
Boundary

This is a route proposer only.

The v19.0 router is intentionally bounded:

no external LLM
no neural dependency
no proof authority
confidence is not proof
low-confidence predictions abstain
routed calls still go through TSCall, risk gates, adapters, verifier boundaries, and receipts
candidate graph contamination remains zero
Release claim

v19.0.0 proves TS-AGL can learn a tiny router from its own trace-mined dataset while preserving the rule that learned routing is not proof authority.
