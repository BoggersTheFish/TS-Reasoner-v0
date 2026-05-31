# TS-AGL Cross-Domain Arena

v13.0.0 proves that TS-AGL can coordinate one natural-language request across multiple taught domains.

The arena routes one broad request through:

- `git_repo`
- `filesystem`
- `ts_reasoner`

The call surface remains:

```text
LanguageMove -> TSCall -> ResultPacket -> rendered reply
Demo command
python3 scripts/run_ts_agl_cross_domain_arena.py
Evaluation command
python3 scripts/evaluate_ts_agl_cross_domain_arena.py
Boundary

This is not broad autonomous agency.

The v13.0 arena is intentionally bounded:

no external LLM
read-only operations only
no proof authority inside language routing
no autonomous risky execution
no accepted graph mutation by the language layer
all outputs are receipt-backed
Release claim

v13.0.0 crosses a major architectural threshold:

one natural-language request
  -> multiple taught domains
  -> multiple typed operations
  -> combined cross-domain receipt

This is the first TS-AGL arena where the substrate is not just routing one operation, but coordinating a small multi-domain workflow.
