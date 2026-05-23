# TS-Reasoner v1.0 Limitations

TS-Reasoner v1.0 is a stable public trace-contract release. It is not a large
model, a formal theorem prover, or a broad benchmark result.

## Known Technical Limits

- Relation parsing is regex-based and expects compact terms such as
  `need_water`; multi-word terms are not generally normalized.
- Positive universal `all/all` proof chains are supported; negative transitive
  chains are not yet closed.
- `some` to `all` upgrades are treated conservatively and should usually repair
  to insufficiency.
- Contradiction checks are local heuristic checks over extracted claims.
- Circularity checks are step-level and do not fully model repeated or
  paraphrased premise text.
- `unless`, counterfactuals, modality, temporal scope, and disjunction are
  outside the v1 reasoning surface.
- The CIG is an inspectable provenance/tension graph, not a complete formal
  semantics.
- The TensionLM bridge treats neural output as proposal text only. TS-Reasoner
  remains the verifier and may reject or repair neural completions.
- The TensionProofLM smoke receipt is a data/eval contract check, not a trained
  22M model release.

## Public Claim Boundary

The v1.0 claim is:

> The JSON trace contract, benchmark runner, and known-limit receipts are stable
> enough for another technical reader to inspect or build on.

The v1.0 claim is not:

- general reasoning competence,
- benchmark-grade proof solving,
- language-model generation quality,
- complete contradiction handling.
- completed TensionProofLM-22M training.
