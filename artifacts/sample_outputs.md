# TS-Reasoner-v0 Sample Outputs

## direct_contradiction: invalid

Question: If all A are C and no A are C, are all A C?

Answer: Contradiction detected; no stable answer follows.

Selected chain: `candidate_a_contradiction_aware`

Global tension: `0.1833`

Candidate repair paths: `3`

## invalid_quantifier_jump: invalid

Question: If some A are B and all B are C, are all A C?

Answer: Not enough information.

Selected chain: `candidate_cautious`

Global tension: `0.0000`

Candidate repair paths: `1`

## missing_premise: invalid

Question: Are all A C?

Answer: Not enough information.

Selected chain: `candidate_cautious`

Global tension: `0.4000`

Candidate repair paths: `2`

## repair_loop: invalid

Question: If some pilots are engineers and all engineers are careful, are all pilots careful?

Answer: Not enough information.

Selected chain: `candidate_cautious`

Global tension: `0.0000`

Candidate repair paths: `1`

## valid_syllogism: valid

Question: If all A are B and all B are C, are all A C?

Answer: all A are C.

Selected chain: `candidate_cautious`

Global tension: `0.0000`

Candidate repair paths: `0`
