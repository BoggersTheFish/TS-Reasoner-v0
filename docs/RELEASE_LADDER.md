
TS-Reasoner Release Ladder

This document summarizes the public TS-Reasoner ladder from exported candidate
ingestion to learned candidate adversarial stress.

v1.5.0: Real Exported TensionLM Sample

A real exported TensionLM-side sample was evaluated through the existing
TS-Reasoner adapter. The system did not load TensionLM directly. Exported text
remained candidate data.

v1.6.0: TensionLM Export Set Evaluation

A small set of exported TensionLM-side samples was evaluated through the same
adapter boundary. The set preserved accepted, rejected, abstained, and malformed
cases instead of hiding failures.

v1.7.0: Deeper-Chain Support Repair

The verifier repaired the deeper positive all/all chain limitation exposed by
the v1.6 export set. Multi-hop A -> B -> C -> D support can close inside the
typed verifier boundary, while reverse inference and identity collapse remain
blocked.

v2.0.0: Learned Candidate Model

A tiny dependency-light learned candidate model was added before the typed
verifier. It ranks/proposes structured candidate claims and predicts
channel/resolver signals, but it is not proof authority.

v2.1.0: Learned Candidate Model Adversarial Stress

The learned candidate model was stress-tested with high-confidence wrong,
malformed, unsupported, reverse, contradiction, identity-collapse,
distractor-heavy, and missing-provenance candidates.

Core boundary result:

candidate_graph_contamination_count: 0
accepted_without_typed_support_count: 0
high_confidence_bad_block_rate: 1.0
unsupported_abstained_count: 6
trace_schema_validity: 1.0

The claim is not that every bad candidate gets a hard typed rejection. Some are
safely blocked by abstention. The claim is that adversarial candidates do not
become proof without typed support.

Current Direction

The next useful research step is a same-case comparison between learned
candidate proposals and exported TensionLM-style proposals, while preserving the
same typed verifier boundary.

v2.4.0 — Natural Language Claim Ingestion

v2.4.0 adds bounded natural-language claim ingestion.

The release bridges simple natural-language reasoning prompts into canonical relation-shaped premises and candidate graph claims, then verifies those candidates through the existing candidate bridge and typed TS-Reasoner channels.

Result:

10 bounded NL cases
parse expectation rate: 1.0
status expectation rate: 1.0
malformed input safe-abstain rate: 1.0
accepted without typed support: 0
candidate graph contamination: 0
trace schema validity: 1.0

Boundary preserved:

no broad NLP claim;
no TensionLM runtime;
no training;
no parser/model confidence as proof;
typed channels remain verifier authority.

## v2.5.0 — Benchmark Harness

v2.5.0 adds a reusable train/dev/test-style benchmark harness across:

- syllogism
- rule deduction
- adversarial invalid inference

Result:

- 28 benchmark cases
- status accuracy: 1.0
- claim accuracy: 1.0
- parse success rate: 0.9642857142857143
- invalid rejection-or-abstention rate: 1.0
- accepted without typed support: 0
- candidate graph contamination: 0
- trace schema validity: 1.0

The parse success rate is intentionally below 1.0 because malformed adversarial input is preserved and safe-abstained.

Boundary preserved:

- bounded benchmark surface;
- no broad NLP claim;
- no external benchmark victory claim;
- no TensionLM runtime;
- no training;
- typed verifier channels remain proof authority.

## v2.6.0 — Candidate Model v2

v2.6.0 trains Candidate Model v2 on candidate sets derived from the v2.5 benchmark harness.

Result:

- candidate ranking accuracy: 1.0
- confidence baseline top accept rate: 0.2632
- learned beats confidence baseline margin: 0.7368
- multi-premise ranking success rate: 1.0
- invalid query rejection-or-abstention rate: 1.0
- supported alternative recovery rate: 1.0
- malformed input non-accept rate: 1.0
- accepted without typed support: 0
- candidate graph contamination: 0
- trace schema validity: 1.0

Boundary preserved:

- Candidate Model v2 ranks candidates only.
- Typed channels remain proof authority.
- No TensionLM runtime.
- No broad NLP claim.
- No neural language model training.

## v2.7.0 — Verifier Trace Training Data

v2.7.0 exports supervised training rows from Candidate Model v2 verifier traces.

Result:

- row count: 91
- accepted rows: 13
- rejected rows: 40
- abstained rows: 38
- has model features: true
- has verifier targets: true
- has boundary metadata: true
- mean proposal quality: 0.2473

Boundary preserved:

- v2.7 exports training data only.
- It does not train a new model.
- Exported rows are not proof.
- Typed verifier channels define target labels.
- Model confidence remains metadata only.
- No TensionLM runtime is loaded.

## v2.8.0 — Training Loop Smoke

v2.8.0 proves that v2.7 verifier trace rows are usable supervised training signal.

Result:

- train accuracy: 1.0
- eval accuracy: 1.0
- majority baseline eval accuracy: 0.4286
- confidence baseline eval accuracy: 0.5714
- learned beats majority margin: 0.5714
- learned beats confidence margin: 0.4286
- row count: 91
- train rows: 35
- eval rows: 56

Boundary preserved:

- smoke-scale training loop only;
- trained status model is not proof authority;
- typed verifier traces define target labels;
- no TensionLM runtime;
- no neural language model training.

