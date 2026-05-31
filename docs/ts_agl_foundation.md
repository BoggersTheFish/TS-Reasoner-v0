# TS-AGL Foundation

TS-AGL means **Artificial General Language**.

This layer is not a new proof authority and not a replacement for the verifier. It is a natural-language syscall layer:

```text
human text
  -> LanguageMove
  -> TSCall
  -> adapter/result
  -> grounded reply
Boundary

v0 guarantees:

no external LLM
language output is not proof
read-only calls can execute automatically
risky calls must be staged/confirmed by caller policy
adapter results are returned as ResultPacket
each demo can emit an AGLTrace receipt
Core claim

Current AI showed the desired interface. TS-AGL rebuilds that interface as inspectable infrastructure.

Language calls.
Graph stores.
Verifier decides.
Renderer speaks.
v0 domains
ts_reasoner
git_repo
filesystem
v0 metrics

The routing evaluator reports:

move_parse_accuracy
operation_routing_accuracy
missing_slot_detection_accuracy
wrong_state_mutation_count
candidate_graph_contamination_count
external_llm_used

The target gate is that routing passes while wrong mutation and contamination remain zero.
