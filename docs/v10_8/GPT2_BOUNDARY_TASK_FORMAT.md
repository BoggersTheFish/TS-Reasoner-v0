# TS-Reasoner v10.8.0: GPT-2 Reasoning Task Format

v10.8 introduces a frozen GPT-2 boundary task format for comparing raw language
completion against verifier-first reasoning.

Each task contains:

- `case_id`
- `prompt`
- `expected_answer`
- `expected_claim`
- `premises`
- `required_channel`
- `trap_type`

The frozen suite contains 100 tasks across direct support, two-hop and
three-hop transitivity, negative exclusion, reverse-inference traps,
unsupported-claim traps, contradiction traps, messy wrappers, confidence traps,
and fluent unsupported traps.

The release gate is `python3 scripts/v10_8/evaluate_gpt2_boundary_task_schema.py`.
