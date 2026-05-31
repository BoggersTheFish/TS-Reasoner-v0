# TS-Reasoner v10.4: Decoupled Global Proof Grid

v10.4 adds local file-based proof-grid exchange. Nodes export canonical JSON
knowledge packs with hash integrity, channel manifests, accepted claims, branch
worlds, repair targets, provenance, and ledger metadata.

Run:

```bash
python3 -m ts_reasoner.runtime_os_cli export-pack --session @data/v10_2/userspace_session.json --out artifacts/proof_grid_pack.json
python3 -m ts_reasoner.runtime_os_cli import-pack --pack @artifacts/proof_grid_pack.json
```

The signature field is metadata-only in this release. Hash integrity is real;
cryptographic identity signing is deferred.
