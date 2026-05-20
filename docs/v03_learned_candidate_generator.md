# v0.3 Learned Candidate Generator Branch

The `v0.3.0-learned-candidate-generator` branch is intentionally narrow.

Goal:

```text
Given a question + premises, generate multiple candidate reasoning chains.
Then pass them through the existing CIG/ranker/repair pipeline.
```

This is not a full LLM release. The learned generator is a small template-proposal model trained from synthetic candidate rows. It learns which candidate-chain templates to propose, while the existing verifier still performs:

- CIG extraction
- tension scoring
- repair suggestion
- low-tension chain selection
- JSON trace export

## Release Ladder

```text
v0.1.0 = deterministic inspectable reasoning trace contract
v0.2.0 = learned tension-ranker experiment inside the same trace contract
v0.3.0 = learned candidate proposal, still verified by CIG/tension/repair
v0.4.0 = generator + ranker loop
v1.0.0 = TS-native proof/reasoning model benchmark release
```

## Scripts

```bash
python3 scripts/train_candidate_generator.py
python3 -m unittest discover
```

Generated artifacts:

- `artifacts/learned_candidate_generator_v03.json`
- `artifacts/learned_candidate_generator_summary.json`

## Caveat

This branch only proves the learned-generator interface. It does not claim robust natural-language candidate generation. The next hardening step should compare proposal recall and verifier-selected answer quality on candidate sets that include both useful and misleading proposals.

