# v2.6.0: Candidate Model v2

Candidate Model v2 trains the existing pure-Python tiny candidate model on candidate sets derived from the v2.5 benchmark harness.

The release goal is narrow:

```text
benchmark prompt
→ generated candidate graph claims
→ Candidate Model v2 ranks candidates
→ typed TS-Reasoner channels verify
→ accept / reject / abstain receipt
What changed

v2.6 adds:

scripts/build_candidate_model_v2_dataset.py
scripts/train_candidate_model_v2.py
scripts/evaluate_candidate_model_v2.py
data/candidate_model_v2_train.jsonl
data/candidate_model_v2_eval.jsonl
data/candidate_model_v2_stress.jsonl
artifacts/candidate_model_v2.json
artifacts/candidate_model_v2_report.json
artifacts/candidate_model_v2_receipt.json
Metrics

Current combined eval+stress metrics:

{
  "candidate_ranking_accuracy": 1.0,
  "confidence_baseline_top_accept_rate": 0.2632,
  "learned_beats_confidence_baseline_margin": 0.7368,
  "multi_premise_ranking_success_rate": 1.0,
  "invalid_query_rejection_or_abstention_rate": 1.0,
  "supported_alternative_recovery_rate": 1.0,
  "malformed_input_non_accept_rate": 1.0,
  "accepted_candidate_support_rate": 1.0,
  "bad_candidate_rejection_rate": 1.0,
  "accepted_without_typed_support_count": 0,
  "candidate_graph_contamination_count": 0,
  "trace_schema_validity": 1.0
}
Why invalid cases can still have accepted candidates

v2.6 is a candidate-ranking release, not a final-answer benchmark release.

Some invalid benchmark queries have a supported alternative candidate. For example, if the invalid query is:

All vehicles are cars?

and the premise says:

All cars are vehicles.

then the invalid query candidate should be rejected, but the supported alternative claim should be accepted.

That is why v2.6 reports both:

invalid_query_rejection_or_abstention_rate
supported_alternative_recovery_rate
Boundary

Candidate Model v2 is not proof authority.

The model ranks candidate graph claims.
Typed verifier channels decide accept/reject/abstain.
Confidence is a baseline/metadata signal only.
No TensionLM runtime is loaded.
No broad NLP claim is made.
No accepted candidate is allowed without typed support.
