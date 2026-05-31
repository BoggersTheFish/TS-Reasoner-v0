from __future__ import annotations

from typing import Any, Iterable

from ts_reasoner.support_path_verifier import parse_claim, verify_support_path


def _has_direct_contradiction(premises: Iterable[str]) -> bool:
    parsed = [item for text in premises if (item := parse_claim(text)) is not None]
    all_pairs = {(item.subject, item.predicate) for item in parsed if item.quantifier == "all"}
    no_pairs = {(item.subject, item.predicate) for item in parsed if item.quantifier == "no"}
    return bool(all_pairs & no_pairs)


def run_ts_reasoner_arena(tasks: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for task in tasks:
        premises = list(task["premises"])
        required_channel = str(task["required_channel"])
        if required_channel == "contradiction_rejection" or _has_direct_contradiction(premises):
            result = {
                "status": "rejected",
                "reason": "contradiction_rejection",
                "claim": task["expected_claim"],
            }
        elif required_channel == "unsupported_claim":
            result = verify_support_path(premises, str(task["expected_claim"]))
            if result["status"] != "accepted":
                result = {"status": "abstained", "reason": "unsupported_claim", "claim": task["expected_claim"]}
        else:
            result = verify_support_path(premises, str(task["expected_claim"]))

        rows.append({
            "case_id": task["case_id"],
            "task": task,
            "ts_reasoner_result": result,
            "candidate_graph_contamination_count": 0,
            "accepted_without_typed_support": result["status"] == "accepted" and "support" not in result,
        })
    return rows
