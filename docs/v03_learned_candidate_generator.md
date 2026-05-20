# v0.3 Learned Candidate Generator Branch

The `v0.3.0-learned-candidate-generator` branch is intentionally narrow.

Goal:

```text
Given a question + premises, generate multiple candidate reasoning chains.
Then pass them through the existing CIG/ranker/repair pipeline.
```

This is not a full LLM release. The learned generator is a small template-proposal model trained from synthetic candidate rows. It is a learned candidate proposal model, not a learned reasoning generator. It learns which candidate-chain templates to propose, while the existing verifier still performs:

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
python3 scripts/evaluate_candidate_generators.py
python3 -m unittest discover
```

Generated artifacts:

- `artifacts/learned_candidate_generator_v03.json`
- `artifacts/learned_candidate_generator_summary.json`
- `artifacts/candidate_generator_coverage.json`

## Safety Fallbacks

The learned proposer has two explicit safety rules:

- If it proposes too few candidates, include the cautious fallback candidate.
- If contradiction is detected in premises and a contradiction-aware candidate is available, force that candidate into the proposal set.

These rules keep the proposal model from narrowing the candidate graph so much that the verifier loses critical paths.

## Coverage Metrics

The candidate-generator eval reports:

- average candidates proposed per task
- percent of tasks where a correct/stable candidate is included
- percent of adversarial tasks where the confident-wrong candidate is suppressed
- percent of contradiction tasks where the contradiction-aware candidate appears

The comparison includes:

- deterministic generator
- learned generator
- learned generator plus safety fallback
- random candidate proposer

Current coverage table:

```text
generator                                avg_candidates  stable_included  adv_suppressed  contradiction_included
deterministic_generator                  2.2500          1.0000           1.0000          1.0000
learned_generator                        1.2500          1.0000           1.0000          1.0000
learned_generator_plus_safety_fallback   2.0000          1.0000           1.0000          1.0000
random_candidate_proposer                1.3393          0.5357           1.0000          0.3571
```

Interpretation:

- The learned proposer is a narrower policy selector over toy chain templates.
- The safety fallback widens the proposal set when the learned proposer is too narrow.
- Contradiction-aware candidates are forced into the set when the deterministic base generator detects contradiction.
- The random proposer shows why proposal coverage matters before CIG/ranker/repair verification.

## Caveat

This branch only proves the learned-generator interface. It evaluates learned candidate selection/proposal over toy chain families, not open-ended reasoning generation. It does not claim robust natural-language candidate generation. The next hardening step should compare proposal recall and verifier-selected answer quality on candidate sets that include both useful and misleading proposals.
