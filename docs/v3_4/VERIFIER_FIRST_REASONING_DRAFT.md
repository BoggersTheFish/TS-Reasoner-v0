# Verifier-First Reasoning: Learning Candidate Selection Without Granting Models Proof Authority

## Abstract

Modern language models often entangle candidate generation, confidence, and proof. TS-Reasoner explores a different boundary: models may propose or rank candidate claims, but typed verifier channels decide whether a claim is accepted, rejected, or abstained.

This draft describes a bounded verifier-first reasoning architecture in which learned candidate models improve proposal ordering while proof authority remains with typed verifier traces.

## Core claim

    Learned candidate selection can improve routing without becoming proof authority.

## Architecture

    input problem
    -> candidate claims
    -> advisory model ranking
    -> typed verifier channels
    -> accept / reject / abstain trace
    -> receipt

## Typed channels

Typed verifier channels prevent scalar tension collapse. Instead of blending all failures into one score, TS-Reasoner separates operational failure modes:

- logic transitivity;
- directionality;
- identity preservation;
- contradiction;
- quantifier/scope mismatch;
- surface structure;
- confidence abstention.

## Boundary

The system rejects three dangerous shortcuts:

1. confidence as proof;
2. candidate edges entering the support graph;
3. learned model prediction overriding typed support.

## Current bounded evidence

v3.0 shows that a verifier-guided candidate model can learn candidate status and likely channel behaviour from verifier-derived rows.

v3.2 adds a cold-reader trace demo that blocks high-confidence wrong candidates while accepting only typed-supported claims.

v3.3 adds an external-format mini-benchmark adapter with wrong_accept_count as the first safety metric.

## Why this matters

A reasoning system that can say "I do not have typed support" is more useful than a system that confidently relaxes into a plausible unsupported answer.

TS-Reasoner is not designed to maximize fluent output. It is designed to preserve the proof boundary.

## Non-claims

This work does not claim:

- broad natural-language understanding;
- general theorem-proving completeness;
- frontier-model superiority;
- production reliability;
- live TensionLM runtime proof authority.

## Research direction

The next step is to connect richer candidate proposers, including TensionLM-style systems, while keeping typed verification as the authority layer.

    TensionLM proposes language-shaped hypotheses.
    TS-Reasoner verifies structure.
