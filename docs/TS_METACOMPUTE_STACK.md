# TS-Metacompute Stack

Tagline:

```text
Verifier-first reasoning over readable state evolution.
```

Subtagline:

```text
Graphs store meaning. Spectral fields expose tension. Substrates propose.
Verifiers decide. Receipts prove what happened.
```

## Endgame

The target architecture is not:

```text
User -> LLM -> answer
```

It is:

```text
user / file / code / model output
-> TS-AGL language-to-operation compiler
-> TS graph / common-ground state
-> metacompute substrate scheduler
-> readable substrate evolution
-> deterministic reader
-> typed verifier
-> repair / memory / receipt
-> answer / action
```

The LLM or candidate model is one proposer. The accepted reasoning authority is:

```text
state + constraints + readable evolution + verifier
```

## Layers

Layer 0 is TS-Core, the proof authority. It owns typed claims, relations,
tension channels, support paths, contradiction checks, abstention, repair
targets, and receipts. Its job is strictness, not cleverness.

Layer 1 is TS-AGL. Language becomes controlled operations:

```text
"What do we know about X?" -> TSCall(query_common_ground, target=X)
"Why did you reject that?" -> TSCall(explain_rejection, claim_id=...)
"Try to repair this contradiction." -> TSCall(generate_repair_candidates, contradiction_id=...)
```

Layer 2 is common-ground memory. Memory stores status, not just text:

```text
accepted != proposed
rejected != forgotten
unsupported != false
candidate != proof
```

Layer 3 is the metacompute substrate scheduler. It asks which substrate can
produce the cheapest useful reading while preserving the proof boundary.

## Substrates

Current implemented substrates:

- **Spectral/Fourier reader**: signed graph -> signed Laplacian -> modes,
  tension, residual edges, repair ranking.
- **Photonic simulation**: signed graph -> frequency-slot state ledger ->
  constructive/destructive interference read.
- **Temporal tension bridge**: late contradiction -> backward assumption
  probability updates recorded in a tamper-evident ledger.
- **Resonance network**: solved constraint shape -> low-bandwidth telemetry
  alignment across nodes without answer-packet transmission.
- **Unified field kernel**: generation, fuzzing, and firewall checks behind a
  single zero-tension verifier gate.
- **Lazy universe orchestrator**: composes the cognitive physics substrates and
  emits only verifier-supported zero-tension outputs.

Planned substrate classes:

- **Symbolic verifier kernel**: typed proof authority, contradiction gates, support paths.
- **Phase/oscillator kernel**: support as phase alignment, conflict as anti-alignment, stable basin reads.
- **Grid/cellular kernel**: cheap local updates, tension weather maps, parallel relaxation.
- **Virtual field kernel**: visual field-scope surface for intuition and demonstrations.
- **Neural candidate kernel**: LLM/TensionLM/tiny model proposals that remain candidate data.

The rule is the same for every substrate:

```text
substrates propose / expose / rank
typed verifier accepts / rejects / abstains
receipts record what changed
```

## Implemented v0.1 Slice

TS-SpectralCompute v0.1 is implemented in:

- `ts_metacompute/scheduler.py`
- `ts_metacompute/spectral/signed_graph.py`
- `ts_metacompute/spectral/laplacian.py`
- `ts_metacompute/spectral/modes.py`
- `ts_metacompute/spectral/residuals.py`
- `ts_metacompute/spectral/repairs.py`
- `ts_metacompute/spectral/receipts.py`
- `ts_metacompute/spectral/evaluate.py`

Evaluation:

```bash
python3 scripts/evaluate_spectral_metacompute.py
```

The v0.1 gate covers:

- coherent support chain
- contradiction triangle
- planted bad edge
- provenance-weighted bad edge
- ambiguous frustrated loop
- repair split
- noise injection
- multi-component graph

## Implemented Cognitive Physics Slice

The TS-OS Cognitive Physics Engine is implemented in:

- `ts_reasoner/cognitive_physics_engine.py`
- `scripts/evaluate_cognitive_physics_engine.py`
- `tests/test_cognitive_physics_engine.py`
- `docs/cognitive_physics_engine.md`

Evaluation:

```bash
python3 scripts/evaluate_cognitive_physics_engine.py
```

The gate covers:

- photonic frequency-slot state storage;
- simulated interference cancellation for contradictions;
- temporal tension back-propagation over assumption probabilities;
- resonance telemetry that transmits constraint shape, not answers;
- unified field emission only for zero-tension verifier-supported state;
- lazy universe orchestration over the full substrate stack;
- zero accepted-without-verifier-support events.

The cognitive physics layer uses roadmap names such as
`Photonic_State_Ledger`, `Retrocausal_Fuzzer`,
`Spectral_Coupling_Telepathy`, `Unified_Field_Kernel`, and
`The_Lazy_Universe_Engine`. In this repository those names refer to
deterministic substrate simulators and receipts, not literal hardware or
physical claims.

Metrics:

- coherence detection rate
- contradiction detection rate
- planted bad edge top-1 rate
- repair relief accuracy
- ambiguous-loop correct abstention
- wrong accept count
- accepted without verifier support count
- receipt schema validity

## Boundary

Allowed claim:

```text
TS is a verifier-first architecture for inspectable reasoning over graph-structured claims.
```

Strong but bounded claim:

```text
Metacompute substrates can expose useful tension/coherence signals that guide repair, search, and candidate selection.
```

Not claimed:

```text
We solved AGI.
The system understands everything.
Spectral modes create truth.
Fields think.
```

The killer gate remains:

```text
Spectral reader may suggest repairs,
but it must never accept truth without typed verifier support.
```
