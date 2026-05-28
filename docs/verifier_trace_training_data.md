# v2.7.0: Verifier Trace Training Data

v2.7.0 exports supervised training rows from Candidate Model v2 verifier traces.

The goal is to turn typed verifier outcomes into reusable training targets:

```text
candidate proposal / ranking
→ typed verifier result
→ channel/failure reason
→ supervised training row
Exported row contents

Each row includes:

case id and split
candidate id and claim
candidate confidence
model prediction
model features
verifier status
verifier reason
typed channel names
typed runtime context
training target
explicit boundary metadata
Training target

The training target includes:

proposal_quality
target_status
target_channels
should_accept
should_reject
should_abstain
failure_reason
typed error flags such as:
is_reverse_error
is_identity_error
is_quantifier_error
is_contradiction_error
is_malformed_error
is_unsupported
Current summary
{
  "row_count": 91,
  "accepted_rows": 13,
  "rejected_rows": 40,
  "abstained_rows": 38,
  "has_model_features": true,
  "has_verifier_targets": true,
  "has_boundary": true
}
Command
python3 scripts/export_verifier_trace_training_data.py

Generated artifacts:

data/verifier_trace_training_data_v27.jsonl
artifacts/verifier_trace_training_data_summary.json
artifacts/verifier_trace_training_data_receipt.json
Boundary

v2.7 does not train a new model.

It exports training data from verifier traces. The exported rows are not proof. They are supervised examples for future training loops where typed verifier channels remain authority.
