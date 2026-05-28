#!/usr/bin/env python3
"""Build a deterministic scaled comparison set for learned-vs-exported candidate evaluation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_case(
    case_id: str,
    input_text: str,
    valid_claim: str,
    bad_claims: list[tuple[str, str, float]],
    tags: list[str],
) -> dict:
    candidates = [
        {
            "candidate_id": f"{case_id}_valid",
            "claim": valid_claim,
            "raw_output": valid_claim,
            "source": "scaled_comparison_generator",
            "confidence": 0.40,
        }
    ]

    labels = {
        f"{case_id}_valid": {
            "claim": valid_claim,
            "status": "accepted",
            "channels": ["logic_transitivity"],
            "resolver": "accept_transitive",
            "reason": "typed transitive support exists",
        }
    }

    for idx, (kind, claim, confidence) in enumerate(bad_claims, start=1):
        candidate_id = f"{case_id}_{kind}_{idx}"
        candidates.append(
            {
                "candidate_id": candidate_id,
                "claim": claim,
                "raw_output": claim,
                "source": "scaled_comparison_generator",
                "confidence": confidence,
            }
        )
        if kind == "reverse":
            labels[candidate_id] = {
                "claim": claim,
                "status": "rejected",
                "channels": ["directionality"],
                "resolver": "reject_reverse",
                "reason": "candidate reverses directed support",
            }
        elif kind == "contradiction":
            labels[candidate_id] = {
                "claim": claim,
                "status": "rejected",
                "channels": ["contradiction"],
                "resolver": "reject_contradiction",
                "reason": "candidate contradicts typed support",
            }
        elif kind == "identity":
            labels[candidate_id] = {
                "claim": claim,
                "status": "rejected",
                "channels": ["identity_preservation"],
                "resolver": "reject_identity",
                "reason": "candidate collapses distinct nodes",
            }
        else:
            labels[candidate_id] = {
                "claim": claim,
                "status": "abstained",
                "channels": ["typed_support"],
                "resolver": "abstain_unsupported",
                "reason": "candidate is not supported by typed channels",
            }

    return {
        "case_id": case_id,
        "split": "scaled_comparison",
        "input_text": input_text,
        "tags": tags,
        "candidates": candidates,
        "labels": labels,
        "comparison_policy": {
            "learned_arm": "TinyCandidateModel ranking_score order",
            "exported_arm": "exported candidate confidence order",
            "authority": "typed verifier result, not either ranker",
        },
    }


def main() -> None:
    chains = [
        ("alpha", "All A are B. All B are C. Are all A C?", "All A are C", "All C are A", "No A are C", "A equals C", "All A are Z"),
        ("beta", "All cats are mammals. All mammals are animals. Are all cats animals?", "All cats are animals", "All animals are cats", "No cats are animals", "cats equals animals", "All cats are machines"),
        ("gamma", "All poets are writers. All writers are artists. Are all poets artists?", "All poets are artists", "All artists are poets", "No poets are artists", "poets equals artists", "All poets are planets"),
        ("delta", "All sparks are hot. All hot are risky. Are all sparks risky?", "All sparks are risky", "All risky are sparks", "No sparks are risky", "sparks equals risky", "All sparks are blue"),
        ("epsilon", "All oak are trees. All trees are plants. Are all oak plants?", "All oak are plants", "All plants are oak", "No oak are plants", "oak equals plants", "All oak are metals"),
        ("zeta", "All robins are birds. All birds are animals. Are all robins animals?", "All robins are animals", "All animals are robins", "No robins are animals", "robins equals animals", "All robins are stones"),
        ("eta", "All coders are builders. All builders are makers. Are all coders makers?", "All coders are makers", "All makers are coders", "No coders are makers", "coders equals makers", "All coders are clouds"),
        ("theta", "All seeds are starters. All starters are causes. Are all seeds causes?", "All seeds are causes", "All causes are seeds", "No seeds are causes", "seeds equals causes", "All seeds are echoes"),
        ("iota", "All moons are bodies. All bodies are objects. Are all moons objects?", "All moons are objects", "All objects are moons", "No moons are objects", "moons equals objects", "All moons are songs"),
        ("kappa", "All proofs are arguments. All arguments are structures. Are all proofs structures?", "All proofs are structures", "All structures are proofs", "No proofs are structures", "proofs equals structures", "All proofs are rivers"),
    ]

    cases = []
    for name, text, valid, reverse, contradiction, identity, unsupported in chains:
        cases.append(
            make_case(
                f"scaled_{name}",
                text,
                valid,
                [
                    ("reverse", reverse, 0.99),
                    ("contradiction", contradiction, 0.97),
                    ("identity", identity, 0.96),
                    ("unsupported", unsupported, 0.94),
                ],
                ["scaled", "comparison", "high_confidence_bad"],
            )
        )

    deeper = [
        ("lambda", "All A are B. All B are C. All C are D. Are all A D?", "All A are D", "All D are A", "No A are D", "A equals D", "All A are Q"),
        ("mu", "All red are warm. All warm are bright. All bright are visible. Are all red visible?", "All red are visible", "All visible are red", "No red are visible", "red equals visible", "All red are silent"),
        ("nu", "All maps are guides. All guides are tools. All tools are objects. Are all maps objects?", "All maps are objects", "All objects are maps", "No maps are objects", "maps equals objects", "All maps are oceans"),
        ("xi", "All tokens are symbols. All symbols are signs. All signs are marks. Are all tokens marks?", "All tokens are marks", "All marks are tokens", "No tokens are marks", "tokens equals marks", "All tokens are gardens"),
        ("omicron", "All gears are parts. All parts are components. All components are things. Are all gears things?", "All gears are things", "All things are gears", "No gears are things", "gears equals things", "All gears are birds"),
    ]

    for name, text, valid, reverse, contradiction, identity, unsupported in deeper:
        cases.append(
            make_case(
                f"scaled_deeper_{name}",
                text,
                valid,
                [
                    ("reverse", reverse, 0.99),
                    ("contradiction", contradiction, 0.98),
                    ("identity", identity, 0.97),
                    ("unsupported", unsupported, 0.95),
                ],
                ["scaled", "comparison", "deeper_chain", "high_confidence_bad"],
            )
        )

    out = ROOT / "data/scaled_learned_vs_exported_candidate_comparison.jsonl"
    out.write_text("".join(json.dumps(case, sort_keys=True) + "\n" for case in cases), encoding="utf-8")
    print(f"wrote {len(cases)} cases to {out}")


if __name__ == "__main__":
    main()
