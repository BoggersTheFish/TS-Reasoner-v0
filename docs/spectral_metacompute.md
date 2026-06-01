# TS-SpectralCompute v0.1

TS-SpectralCompute is the first metacompute substrate in this repo. It reads a
signed TS graph as a constraint system:

- support edges want node states to align
- conflict edges want node states to anti-align
- the signed Laplacian exposes irreducible tension
- residual edges rank local repair pressure
- repair candidates remain candidate actions

The proof boundary is unchanged:

```text
spectral reader -> repair suggestions -> typed verifier -> accepted/rejected/abstained
```

The spectral reader never accepts truth. It emits tension, modes, edge
residuals, and candidate repairs. Acceptance still requires typed verifier
support from the verifier layer.

Run the v0.1 gate:

```bash
python3 scripts/evaluate_spectral_metacompute.py
```

Expected artifacts:

- `artifacts/spectral_metacompute_report.json`
- `artifacts/spectral_metacompute_receipt.json`

Current gate cases:

- coherent support chain
- contradiction triangle
- planted bad edge
- provenance-weighted bad edge
- ambiguous frustrated loop
- repair split
- noise injection
- multi-component graph

Current gate metrics:

- coherence detection rate
- contradiction detection rate
- planted bad edge top-1 rate
- repair relief accuracy
- ambiguous-loop correct abstention
- wrong accept count
- accepted without verifier support count
- receipt schema validity

The current implementation is stdlib-only because TS-Reasoner-v0 currently has
no runtime dependencies. A SciPy backend can replace the small Jacobi eigensolver
once graph sizes justify acceleration, without changing the verifier boundary.
