# TS-Reasoner v11.1.0: Natural Claim Surface Normalization

v11.1.0 expands the bounded claim surface accepted by TS-Reasoner while preserving the verifier-first proof boundary.

## New accepted surfaces

Examples:

- `all generated text is candidate data`
- `every generated output is candidate data`
- `each unsupported claim is repair target`
- `any model confidence signal is generated signal`
- `no generated signal is proof`
- `model confidence is not proof`
- `nothing that is generated signal is proof`
- `generated text is candidate data`

These normalize into the canonical verifier form:

- `all X are Y`
- `no X are Y`

## Boundary

This release does not claim broad natural-language understanding.

It only adds bounded surface normalization before the existing typed support verifier runs. Generated text remains candidate data. Model confidence remains non-proof. Accepted claims still require typed verifier support.
