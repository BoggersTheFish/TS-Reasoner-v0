# v0.9 Proof-Chain Support

v0.9 closes the narrow proof-chain gap exposed by v0.8.

The v0.8 benchmark showed that the full control loop could settle every task,
but failed both `small_proof_chain` cases by relaxing to low-tension
insufficiency answers. The failure was local and inspectable: support checks
only recognized one-hop and two-hop universal bridges.

## Change

v0.9 adds explicit positive universal bridge construction:

```text
all A are B
all B are C
all C are D
=> all A are D
```

The implementation is intentionally narrow. It only handles `all` chains
already normalized into TS-Reasoner relation form. It does not add a general
logic engine, natural-language parser, or broader benchmark claim.

## Receipt

Run:

```bash
python3 scripts/evaluate_v09_proof_chains.py
```

This writes `artifacts/v09_proof_chain_report.json` and compares the current
result against the committed v0.8 receipt.

Current v0.9 result:

- `small_proof_chain/full_control_loop`: `2/2`
- `full_control_loop`: `10/10`
- `ranker_only`: `10/10`

## Remaining Limits

- Positive universal chains only.
- Regex relation extraction only.
- Curated normalized fixture only.
- Toy-scope receipt, not a broad reasoning benchmark.
