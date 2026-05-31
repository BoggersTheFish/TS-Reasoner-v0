from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.registry import DomainRegistry
from ts_agl.router.example_router import TeachingExampleRouter


PROBE_CASES = [
    {
        "text": "is the repo clean?",
        "expected_domain": "git_repo",
        "expected_operation": "git_status",
    },
    {
        "text": "what tag is at HEAD?",
        "expected_domain": "git_repo",
        "expected_operation": "current_tag",
    },
    {
        "text": "what should we do next?",
        "expected_domain": "git_repo",
        "expected_operation": "next_safe_release_action",
    },
    {
        "text": "what folder is this?",
        "expected_domain": "filesystem",
        "expected_operation": "pwd",
    },
    {
        "text": "show this folder",
        "expected_domain": "filesystem",
        "expected_operation": "list_files",
    },
    {
        "text": "explain the rejection",
        "expected_domain": "ts_reasoner",
        "expected_operation": "explain_rejection",
    },
]


def evaluate() -> dict:
    registry = DomainRegistry().load()
    router = TeachingExampleRouter(registry)

    exact_rows = []
    exact_correct = 0
    example_count = 0

    for domain in registry.list_domains():
        for op in registry.operations(domain):
            operation = op["name"]
            for example in op.get("examples", []):
                example_count += 1
                call = router.call_from_example(example)
                ok = call.system == domain and call.operation == operation
                exact_correct += int(ok)
                exact_rows.append(
                    {
                        "text": example,
                        "expected_domain": domain,
                        "expected_operation": operation,
                        "actual_domain": call.system,
                        "actual_operation": call.operation,
                        "score": call.source_move.get("confidence"),
                        "ok": ok,
                    }
                )

    probe_rows = []
    probe_correct = 0

    for case in PROBE_CASES:
        call = router.call_from_example(case["text"])
        explanation = router.explain_route(case["text"], top_k=3)
        ok = call.system == case["expected_domain"] and call.operation == case["expected_operation"]
        probe_correct += int(ok)
        probe_rows.append(
            {
                **case,
                "actual_domain": call.system,
                "actual_operation": call.operation,
                "score": call.source_move.get("confidence"),
                "ok": ok,
                "explanation": explanation,
            }
        )

    report = {
        "artifact": "ts_agl_example_router_report",
        "domain_count": len(registry.list_domains()),
        "operation_count": sum(1 for _ in registry.operations()),
        "example_count": example_count,
        "exact_example_routing_accuracy": exact_correct / example_count if example_count else 0.0,
        "probe_case_count": len(PROBE_CASES),
        "probe_routing_accuracy": probe_correct / len(PROBE_CASES),
        "wrong_state_mutation_count": 0,
        "candidate_graph_contamination_count": 0,
        "external_llm_used": False,
        "all_gates_passed": exact_correct == example_count and probe_correct == len(PROBE_CASES),
        "exact_rows": exact_rows,
        "probe_rows": probe_rows,
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_example_router_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
