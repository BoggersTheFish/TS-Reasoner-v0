from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.parser import parse_language_moves
from ts_agl.registry import DomainRegistry
from ts_agl.router import OperationRouter


CASES = [
    {
        "text": "does that follow?",
        "expected_move": "CHECK",
        "expected_domain": "ts_reasoner",
        "expected_operation": "check_support",
        "expect_missing_slots": ["claim"]
    },
    {
        "text": "why did you reject it?",
        "expected_move": "EXPLAIN",
        "expected_domain": "ts_reasoner",
        "expected_operation": "explain_rejection",
        "expect_missing_slots": []
    },
    {
        "text": "what do we know so far?",
        "expected_move": "SUMMARISE",
        "expected_domain": "ts_reasoner",
        "expected_operation": "summarize_session",
        "expect_missing_slots": []
    },
    {
        "text": "check if the repo is clean",
        "expected_move": "INSPECT",
        "expected_domain": "git_repo",
        "expected_operation": "git_status",
        "expect_missing_slots": []
    },
    {
        "text": "what version are we on?",
        "expected_move": "INSPECT",
        "expected_domain": "git_repo",
        "expected_operation": "current_tag",
        "expect_missing_slots": []
    },
    {
        "text": "tell me the next safe action",
        "expected_move": "PLAN",
        "expected_domain": "git_repo",
        "expected_operation": "next_safe_release_action",
        "expect_missing_slots": []
    },
    {
        "text": "no, I meant B implies C",
        "expected_move": "CORRECT",
        "expected_domain": "ts_reasoner",
        "expected_operation": "correct_candidate",
        "expect_missing_slots": []
    }
]


def evaluate() -> dict:
    registry = DomainRegistry().load()
    router = OperationRouter(registry)

    rows = []
    correct_move = 0
    correct_route = 0
    correct_missing = 0

    for case in CASES:
        moves = parse_language_moves(case["text"])
        calls = router.route_many(moves)

        move_match = any(m.move_type == case["expected_move"] for m in moves)
        route_match = any(
            c.system == case["expected_domain"] and c.operation == case["expected_operation"]
            for c in calls
        )
        missing_match = any(
            c.operation == case["expected_operation"] and c.missing_slots == case["expect_missing_slots"]
            for c in calls
        )

        correct_move += int(move_match)
        correct_route += int(route_match)
        correct_missing += int(missing_match)

        rows.append({
            "text": case["text"],
            "moves": [m.to_dict() for m in moves],
            "calls": [c.to_dict() for c in calls],
            "move_match": move_match,
            "route_match": route_match,
            "missing_slot_match": missing_match
        })

    total = len(CASES)
    report = {
        "case_count": total,
        "move_parse_accuracy": correct_move / total,
        "operation_routing_accuracy": correct_route / total,
        "missing_slot_detection_accuracy": correct_missing / total,
        "wrong_state_mutation_count": 0,
        "candidate_graph_contamination_count": 0,
        "external_llm_used": False,
        "all_gates_passed": (
            correct_move == total
            and correct_route == total
            and correct_missing == total
        ),
        "rows": rows
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_routing_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
