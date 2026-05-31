# TS-Reasoner v10.7.0: Support Path Verifier

v10.7 creates typed support traces from bounded premise graphs instead of
trusting supplied support labels.

Supported channels:

- `direct_support`: `all A are B -> all A are B`
- `transitive_all`: `all A are B + all B are C -> all A are C`
- `negative_exclusion`: `all A are B + no B are C -> no A are C`
- `identity_block`: identity claims do not create fake new knowledge
- `reverse_inference_block`: `all A are B` does not imply `all B are A`

The release gate is `python3 scripts/v10_7/evaluate_support_path_verifier.py`.
