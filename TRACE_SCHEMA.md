# TS-Reasoner v1.0 Trace Schema

TS-Reasoner v1.0 freezes the public JSON trace contract for inspection and
downstream tooling. The contract is intentionally small: the same top-level
fields are emitted by the CLI, benchmark scripts, and optional bridge tools.

## Top-Level Output

Every serialized `ReasonerOutput` object contains these keys:

- `question`: original question string.
- `premises`: explicit premise strings after light cleanup or inference.
- `candidates`: generated reasoning chains before final selection.
- `selected_chain`: the post-loop chain selected by the verifier/ranker.
- `tension_score`: local and global tension for the selected chain.
- `cig_check`: extracted claims, dependencies, contradictions, unsupported
  claims, and circular step ids for the selected chain.
- `repairs`: suggested repairs for the selected chain.
- `final_answer`: selected chain answer string.
- `trace`: telemetry for the pipeline run.

## Required Trace Keys

The v1.0 `trace` object contains:

- `contract_version`: currently `1.0.0`.
- `pipeline`: currently `TS-Reasoner-v0`.
- `input`: original question and premise list.
- `generator`: generator name used to propose candidates.
- `ranker`: ranker class name.
- `tension_coordinator`: coordinator name.
- `operation_router`: router name.
- `selection`: selected chain ids and selection criterion.
- `candidate_scores`: per-candidate initial/post-loop local and global tension.
- `chosen_action`: final operation/status selected by the control loop.
- `rejected_alternatives`: candidates not selected, with tension and rejection reason.
- `settled_answer`: selected answer string.
- `failure_reason`: `null` when settled, otherwise the final stop status.
- `coordinated_tension_field`: selected chain agent/field state.
- `operation_loop`: bounded repair/compression loop for the selected chain.
- `candidate_operation_loops`: loop trace for every candidate.
- `graph_view`: compact node/edge/claim count view for the selected chain.

Optional extensions may add keys under `trace`, but v1 consumers can rely on
the required keys above remaining present and JSON-compatible.

## Compatibility Policy

v1.0 does not promise formal logical completeness. It promises that public
trace consumers can parse the same field names and broad value shapes while the
research code evolves.

Allowed after v1.0:

- additive trace keys,
- new candidate generators,
- new benchmark artifacts,
- new issue kinds in `tension_score.issues`.

Not allowed without a new schema version:

- removing top-level output keys,
- renaming required trace keys,
- changing required trace fields from JSON objects/lists/scalars into
  incompatible shapes.

## Minimal Example

```json
{
  "question": "If all A are B and all B are C, are all A C?",
  "premises": ["All A are B.", "All B are C."],
  "final_answer": "all A are C.",
  "trace": {
    "contract_version": "1.0.0",
    "pipeline": "TS-Reasoner-v0",
    "input": {
      "question": "If all A are B and all B are C, are all A C?",
      "premises": ["All A are B.", "All B are C."]
    },
    "generator": "DeterministicHeuristicGenerator",
    "ranker": "HeuristicTensionRanker",
    "operation_router": "OperationRouter",
    "settled_answer": "all A are C.",
    "failure_reason": null
  }
}
```

The full object also includes chains, CIG checks, tension scores, repairs, and
operation-loop telemetry.

## Trace Bridge Fields

Downstream TS systems should treat the following as the bridge contract:

- input: `trace.input`
- candidate steps: `candidates[*].steps`
- local tension: `tension_score.local_tension` and
  `trace.candidate_scores[*].local_tension`
- global tension: `tension_score.global_tension` and
  `trace.candidate_scores[*].global_tension`
- chosen action: `trace.chosen_action`
- rejected alternatives: `trace.rejected_alternatives`
- settled answer: `trace.settled_answer`
- failure reason: `trace.failure_reason`

Optional integrations, such as the TensionLM proposal bridge, may add their own
namespaced trace keys without changing the stable fields above.
