# TS-Reasoner v8.2.0: Missing Bridge Synthesizer

v8.2.0 adds a bounded missing-bridge synthesizer.

The purpose is to turn unsupported claims into explicit candidate premises needed for support.

Example:

Known:

all cats are animals

Target:

all cats are mortal

Missing bridge:

all animals are mortal

## What this proves

The system can identify when a target is already supported, when it needs one bridge, and when it needs a bounded two-hop bridge.

Generated bridges are candidate repair data.

They are not proof.

## Boundaries

v8.2.0 is not broad natural-language understanding.

It is not a general theorem prover.

It does not make generated bridges true.

Typed verifier support remains the proof boundary.
