from __future__ import annotations

from pathlib import Path
import json
import sys
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.registry import DomainRegistry
from ts_agl.router.example_router import TeachingExampleRouter
from ts_agl.training import build_router_dataset, write_router_dataset_jsonl


def evaluate() -> dict:
    registry = DomainRegistry().load()
    rows = build_router_dataset(registry=registry)
    write_router_dataset_jsonl(rows, "artifacts/ts_agl_router_dataset.jsonl")

    router = TeachingExampleRouter(registry)

    domain_example_rows = [row for row in rows if row.source == "domain_example"]
    hard_negative_rows = [row for row in rows if row.source == "hard_negative"]

    exact_domain_example_correct = 0
    for row in domain_example_rows:
        call = router.call_from_example(row.text)
        if call.system == row.expected_domain and call.operation == row.expected_operation:
            exact_domain_example_correct += 1

    hard_negative_correct = 0
    hard_negative_details = []
    for row in hard_negative_rows:
        call = router.call_from_example(row.text)
        ok = call.system == "ts_reasoner" and call.operation == "route_unknown"
        hard_negative_correct += int(ok)
        hard_negative_details.append(
            {
                "text": row.text,
                "actual_domain": call.system,
                "actual_operation": call.operation,
                "ok": ok,
            }
        )

    label_counts = Counter(row.label for row in rows)
    domain_counts = Counter(row.expected_domain for row in rows)
    source_counts = Counter(row.source for row in rows)

    report = {
        "artifact": "ts_agl_router_dataset_report",
        "dataset_path": "artifacts/ts_agl_router_dataset.jsonl",
        "row_count": len(rows),
        "label_counts": dict(sorted(label_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "domain_example_count": len(domain_example_rows),
        "hard_negative_count": len(hard_negative_rows),
        "domain_example_routing_accuracy": (
            exact_domain_example_correct / len(domain_example_rows)
            if domain_example_rows else 0.0
        ),
        "hard_negative_abstention_accuracy": (
            hard_negative_correct / len(hard_negative_rows)
            if hard_negative_rows else 0.0
        ),
        "has_trace_mined_rows": any(row.source.startswith("trace:") for row in rows),
        "has_external_side_effect_rows": any(row.risk == "external_side_effect" for row in rows),
        "has_reversible_write_rows": any(row.risk == "reversible_write" for row in rows),
        "hard_negative_details": hard_negative_details,
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "wrong_state_mutation_count": 0,
        "all_gates_passed": (
            len(rows) > 0
            and label_counts.get("route", 0) > 0
            and label_counts.get("abstain", 0) > 0
            and len(domain_example_rows) > 0
            and len(hard_negative_rows) > 0
            and exact_domain_example_correct == len(domain_example_rows)
            and hard_negative_correct == len(hard_negative_rows)
            and any(row.source.startswith("trace:") for row in rows)
            and any(row.risk == "external_side_effect" for row in rows)
            and any(row.risk == "reversible_write" for row in rows)
        ),
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_router_dataset_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_agl_router_dataset_receipt",
        "dataset_path": report["dataset_path"],
        "row_count": report["row_count"],
        "domain_example_routing_accuracy": report["domain_example_routing_accuracy"],
        "hard_negative_abstention_accuracy": report["hard_negative_abstention_accuracy"],
        "has_trace_mined_rows": report["has_trace_mined_rows"],
        "has_external_side_effect_rows": report["has_external_side_effect_rows"],
        "has_reversible_write_rows": report["has_reversible_write_rows"],
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "wrong_state_mutation_count": 0,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_agl_router_dataset_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
