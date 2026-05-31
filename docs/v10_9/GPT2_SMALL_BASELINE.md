# TS-Reasoner v10.9.0: GPT-2-small Baseline Harness

v10.9 freezes a reproducible GPT-2-small baseline on the TS verifier-first
boundary task suite.

The harness treats GPT-2-small as an untrusted raw language proposer and scores
only parsed `ANSWER`, `CLAIM`, `SUPPORT`, and `STATUS` fields. The default repo
path is an offline frozen baseline fixture so the release gate is reproducible
without network or model downloads.

The baseline is scored on answer accuracy, claim accuracy, support-path
accuracy, contradiction rejection, unsupported abstention, wrong accepts, and
format parse rate.

The release gate is `python3 scripts/v10_9/evaluate_gpt2_small_baseline.py`.
