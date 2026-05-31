# TS-AGL Domain Teaching Protocol

v7.2 turns TS-AGL domain packs into validated teaching objects.

A domain pack teaches the fixed TS-AGL substrate:

- what objects exist
- what relations matter
- what operations are allowed
- what risk level each operation has
- what language examples should route to each operation
- what failure modes matter

## Principle

```text
Build the substrate once. Teach it domains forever.

The domain pack is not proof authority. It is a teachable interface contract.

Required manifest fields

Each domain manifest must define:

{
  "domain": "git_repo",
  "description": "Local git repository inspection operations for TS-AGL.",
  "node_types": ["repo", "branch"],
  "edge_types": ["points_to"],
  "operations": [],
  "failure_modes": []
}

Each operation must define:

{
  "name": "git_status",
  "description": "Inspect local git worktree and branch state.",
  "required_inputs": [],
  "risk": "read_only",
  "requires_confirmation": false,
  "examples": ["is the repo clean?"]
}
Allowed risk levels
read_only
reversible_write
destructive_write
external_side_effect

Any operation above read_only must require confirmation.

Validation command
python3 scripts/validate_ts_agl_domain_packs.py

The report is written to:

artifacts/ts_agl_domain_pack_validation_report.json
Boundary

v7.2 validates the teaching contract. It does not claim broad natural language understanding, autonomous execution, or proof authority in the language layer.
