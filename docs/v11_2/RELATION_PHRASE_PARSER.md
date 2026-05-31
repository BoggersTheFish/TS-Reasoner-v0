# TS-Reasoner v11.2.0: Relation Phrase Parser

v11.2.0 expands bounded claim normalization from natural copula forms into bounded relation phrases.

Examples:

- `fish belongs to animals`
- `salmon is a kind of fish`
- `candidate data is a type of untrusted material`
- `generated text counts as candidate data`
- `typed support implies proof authority`
- `accepted proof requires typed support`
- `model confidence cannot be proof`
- `candidate data excludes proof`

These normalize into canonical verifier forms:

- `all X are Y`
- `no X are Y`

## Boundary

This is not broad natural-language understanding.

Relation phrases become candidate verifier claims. The typed support verifier still decides whether a claim is accepted, rejected, or abstained. Generated text and model confidence remain non-proof.
