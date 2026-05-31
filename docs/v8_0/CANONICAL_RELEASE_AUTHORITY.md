
TS-Reasoner v8.0.2: Canonical Release Authority

v8.0.2 adds a machine-readable release authority layer for TS-Reasoner.

The purpose is simple:

artifact reality must match public claim surface

Earlier TS-Reasoner work produced receipt-backed capability layers, including verifier-first candidate handling, TS-Chat persistence, repair memory, provenance, knowledge packs, session arenas, and long-run self-repair stress tests.

The new v8.0.2 layer makes release truth explicit instead of relying on scattered README, website, issue, and ecosystem-map wording.

What v8.0.2 adds
release_authority.json
internal release-surface audit
stale current-release detection
forbidden overclaim detection
optional sibling-surface visibility for TS-Start-Here and boggersthefish-site
release authority report
release authority receipt
unit tests for authority sync
What this proves

v8.0.2 proves that TS-Reasoner can audit whether its own public/internal release surface agrees with its canonical release authority.

It does not prove broad reasoning ability.

Previous verified baseline

The previous concrete stress baseline is v6.9.0 long-run self-repair stress.

Expected preserved boundary:

external_llm_used == false
candidate_graph_contamination_count == 0
generated_text_is_not_proof == true
repair_target_is_not_proof == true
knowledge_pack_import_is_not_proof == true
Proof boundary

TS-Reasoner continues to enforce:

candidate generation != proof
model confidence != proof
generated text != proof
typed verifier support = proof boundary
release receipts are required for public release claims
Boundaries

v8.0.2 is a release-authority and truth-surface audit layer.

It is not a broad capability claim, not a broad natural-language understanding claim, not a general theorem-proving claim, and not proof that model-generated text can enter common ground without verification.

Why this matters

The next failure mode is not only bad reasoning.

It is truth drift:

README says one thing
site says another
release receipt says another
issues say another

v8.0.2 introduces the authority layer needed before the v8 immune-system releases:

v8.1 contradiction repair policy engine
v8.2 missing bridge synthesizer
v8.3 provenance-weighted repair decisions
v8.4 branching worlds runtime
v8.5 knowledge pack contracts
v8.6 reasoning diff/patch language
v8.7 audit cockpit
v8.8 adversarial state fuzzer
v8.9 immune system mega-arena

