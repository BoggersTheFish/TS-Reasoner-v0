# TS-Reasoner v11.4.0: Procedural Reasoning Curriculum

v11.4.0 reduces dependence on hand-built benchmark cases.

It generates deterministic verifier-first reasoning tasks from graph templates, relation surfaces, trap types, and paragraph wrappers.

Generated families include:

- direct support
- 2-hop transitive support
- 3-hop transitive support
- 5-hop transitive support
- negative exclusion
- reverse inference traps
- identity traps
- unsupported targets
- direct contradictions
- paragraph-wrapped transitive tasks
- paragraph-wrapped unsupported tasks
- paragraph-wrapped reverse traps

Each generated task has:

- canonical expected claim
- premise list
- required verifier channel
- trap label
- deterministic case id
- prompt surface

## Boundary

This is a deterministic synthetic curriculum generator, not proof of broad open-domain reasoning.

The verifier remains proof authority. Generated tasks are only useful if their labels replay through the verifier and the receipts show zero wrong accepts, zero accepted-without-support, and zero candidate graph contamination.
