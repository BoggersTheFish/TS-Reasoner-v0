# TS Project Curriculum Pack v1

v31.0.0 teaches TS-Reasoner its own project domain as bounded curriculum.

This is the first post-v30 teaching pack:

```text
Built:
- verifier boundary
- typed proof support
- candidate/proposer separation
- router/action surface
- local OS loop
- risk gates
- confirmation gates
- receipts
- domain teaching contract
- TS Project Domain Pack v1

Not fully built:
- open-ended memory growth
- autonomous concept formation
- self-training over arbitrary new domains
- long-term weighted knowledge evolution
- safe promotion from repeated experience into durable belief
```

The v31 claim is intentionally narrow:

```text
Yes, TS-Reasoner is ready to be taught through bounded curriculum packs.
No, TS-Reasoner is not ready for free self-learning.
```

## Run

```bash
python3 scripts/evaluate_ts_project_curriculum.py
```

This writes:

- `artifacts/ts_project_curriculum_report.json`
- `artifacts/ts_project_curriculum_receipt.json`

## Domain Objects

The domain pack teaches these project concepts:

- repo
- release
- artifact
- receipt
- claim
- proof boundary
- unsafe overclaim
- next safe action
- stale public surface
- missing receipt
- domain lesson

## Operations

The curriculum exposes project operations through typed TSCalls:

- `ts_project.inspect_project_state`
- `ts_project.explain_release_state`
- `ts_project.find_missing_receipts`
- `ts_project.detect_stale_public_surface`
- `ts_project.reject_unsafe_overclaim`
- `ts_project.inspect_proof_boundary`
- `ts_project.suggest_next_safe_release_action`
- `ts_project.summarize_curriculum_boundary`
- `ts_project.promote_lesson_candidate`

The final operation is a reversible write and requires confirmation. It proves that repeated experience or language instruction does not become durable belief on its own.

## Acceptance Gates

The v31 evaluator requires:

- manifest validates;
- TS Project domain pack loads;
- project objects are present;
- examples route to `ts_project` operations;
- project state is inspected;
- missing receipt detection works;
- unsafe self-learning overclaim is rejected;
- proof boundary is visible;
- bounded curriculum is distinguished from free self-learning;
- stale public surface check is clear;
- unconfirmed lesson promotion is blocked;
- no external LLM is used;
- no external side effect is performed;
- no network call is performed;
- candidate graph contamination remains zero.

## Boundary

Domain packs teach routing and operation contracts. They are not proof authority.

Language examples may propose routes. Router scores may select operations. Repeated experience may identify candidate lessons. None of that becomes accepted knowledge without verifier support, confirmation when required, and receipts.
