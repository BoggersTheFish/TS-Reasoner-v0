# v3.2 Cold-Reader Demo Trace

Premises:

- All dogs are mammals.
- All mammals are animals.

Question: Are all dogs animals?

Core boundary:

    candidate confidence is metadata
    typed verifier support is proof authority
    candidate edges do not enter the proof-support graph

## Candidate outcomes

### valid_transitive

Claim: All dogs are animals.

Model confidence: 0.41

Verifier status: accepted

Reason: Two-hop all/all transitive support exists.

Typed channels:

- logic_transitivity: supports dogs -> mammals -> animals
- directionality: query direction preserved
- identity_preservation: no identity collapse
- surface_structure: claim is inferred, not directly stated

### reverse_inference_trap

Claim: All animals are dogs.

Model confidence: 0.94

Verifier status: rejected

Reason: Reverse inference is not licensed by the premises.

Typed channels:

- directionality: blocks reverse inference animals -> dogs
- logic_transitivity: no support path animals -> dogs

### identity_collapse_trap

Claim: Dogs are animals because dogs and animals are identical.

Model confidence: 0.88

Verifier status: rejected

Reason: Class inclusion is not identity.

Typed channels:

- identity_preservation: blocks class inclusion becoming identity
- surface_structure: premises support inclusion, not equivalence

### weak_partial_claim

Claim: Some dogs are animals.

Model confidence: 0.77

Verifier status: abstained

Reason: The system avoids accepting a weaker reformulation as the queried answer.

Typed channels:

- confidence_abstention: candidate is weaker or different than the queried universal claim
- surface_structure: claim shape does not match target proof obligation
