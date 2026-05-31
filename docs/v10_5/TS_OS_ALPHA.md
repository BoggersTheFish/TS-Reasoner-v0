# TS-Reasoner v10.5.0: TS-OS Alpha

v10.5.0 integrates the v10.1-v10.4 surfaces into a bounded TS-OS Alpha flow:
userspace proposal, microkernel gate, branch-world continuum, proof-grid export,
local import, and final receipt.

Run:

```bash
python3 -m ts_reasoner.runtime_os_cli alpha --scenario @data/v10_5/ts_os_alpha_scenario.json
```

Public release claim:

TS-OS Alpha treats probabilistic models as untrusted userspace proposers, routes
all mutations through a verifier microkernel, isolates contradictions into
branch worlds, and exchanges receipt-backed knowledge packs through local
verifier gates.
