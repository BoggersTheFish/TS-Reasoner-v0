# TS-AGL Trace-Mined Router Dataset

v18.0.0 adds a trace-mined router dataset for TS-AGL.

The dataset is built from:

- validated domain-pack language examples
- AGL arena receipts/traces
- workflow/action traces
- hard-negative abstention examples

The output is a JSONL dataset:

```text
artifacts/ts_agl_router_dataset.jsonl
Commands
python3 scripts/build_ts_agl_router_dataset.py
python3 scripts/evaluate_ts_agl_router_dataset.py
Boundary

This is not a learned router yet.

The v18.0 dataset is intentionally bounded:

no external LLM
no model training
no proof authority inside routing
dataset rows are supervised routing examples only
hard negatives train/measure abstention behavior
candidate graph contamination remains zero
Release claim

v18.0.0 turns TS-AGL receipts and domain packs into reusable routing supervision. This prepares the ground for a later learned router while keeping proof authority with typed verifier support.
