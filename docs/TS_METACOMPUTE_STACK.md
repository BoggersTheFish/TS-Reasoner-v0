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

Current implemented substrate:

- **Spectral/Fourier reader**: signed graph -> signed Laplacian -> modes,
  tension, residual edges, repair ranking.

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

