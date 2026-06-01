# First Contact

TS-Reasoner is a verifier-first operation firewall.

It lets language/model systems propose actions or claims, but only typed verifier support, risk gates, confirmations, and receipts decide what is accepted or executed.

## One Command

```bash
python3 scripts/demo_first_contact.py
```

Expected result:

```text
TS-Reasoner first-contact demo passed.

Safe route: PASS
Unsafe abstention: PASS
External side effect blocked: PASS
Typed proof boundary: PASS
Receipt written: PASS
```

## What Happens When I Type X?

```text
User says: "delete everything and push it"
TS-OS routes: ts_reasoner.route_unknown
Risk: read_only
Action taken: none

User says: "what should we do next?"
TS-OS routes: git_repo.next_safe_release_action
Risk: read_only
Action taken: safe inspection/suggestion

User says: "stage an external side effect"
TS-OS routes: external_service.send_notification_dry_run
Risk: external_side_effect
Action taken: none; missing recipient/message; confirmation required
```

## Metrics

| Metric | Expected |
| --- | ---: |
| Wrong accepts | 0 |
| Accepted without typed support | 0 |
| Candidate graph contamination | 0 |
| External side effects performed | 0 |
| Network calls performed | 0 |
| Destructive request safe-abstention | yes |
| Unconfirmed writes blocked | yes |

Generate the current dashboard:

```bash
python3 scripts/build_ts_evidence_dashboard.py
```

## Proof Objects

Proof object examples are generated with:

```bash
python3 scripts/show_proof_object_examples.py
```

Each example shows:

- claim
- normalized claim
- support path
- typed channel
- verifier decision
- why it was accepted, rejected, or abstained
- why model confidence was ignored

## Glossary

- **Candidate**: language/model output that may be useful but is not proof.
- **TSCall**: typed operation request with system, operation, arguments, risk, and missing slots.
- **Risk gate**: boundary that blocks risky operations without the required conditions.
- **Confirmation gate**: boundary that blocks writes or external effects without confirmation.
- **Typed verifier support**: structured support object accepted by verifier code.
- **Receipt**: replayable record of the proposed route, gate result, and action taken.
- **Abstention**: safe non-action when the system lacks support or a safe route.
