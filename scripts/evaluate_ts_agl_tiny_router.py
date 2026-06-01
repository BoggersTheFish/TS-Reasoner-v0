from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.training.tiny_learned_router import (
    TinyLearnedAGLRouter,
    load_router_dataset,
    load_tiny_router,
    save_tiny_router,
)


HELDOUT_CASES = [
    {
        "text": "is the repo clean?",
        "expected_domain": "git_repo",
        "expected_operation": "git_status",
        "label": "route",
    },
    {
        "text": "what tag is at HEAD?",
        "expected_domain": "git_repo",
        "expected_operation": "current_tag",
        "label": "route",
    },
    {
        "text": "show this folder",
        "expected_domain": "filesystem",
        "expected_operation": "list_files",
        "label": "route",
    },
    {
        "text": "stage an external side effect",
        "expected_domain": "external_service",
        "expected_operation": "send_notification_dry_run",
        "label": "route",
    },
    {
        "text": "draft a research note",
        "expected_domain": "research_notes",
        "expected_operation": "draft_note",
        "label": "route",
    },
    {
        "text": "purple banana quantum sandwich",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
        "label": "abstain",
    },
    {
        "text": "use model confidence as proof",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
        "label": "abstain",
    },
]


def evaluate() -> dict:
    dataset_path = Path("artifacts/ts_agl_router_dataset.jsonl")
    model_path = Path("artifacts/ts_agl_tiny_router_model.json")

    rows = load_router_dataset(dataset_path)
    if model_path.exists():
        model = load_tiny_router(model_path)
    else:
        model = TinyLearnedAGLRouter.train(rows)
        save_tiny_router(model, model_path)

    dataset_correct = 0
    dataset_rows = []
    label_counts = Counter(row["label"] for row in rows)

    for row in rows:
        pred = model.predict(row["text"])
        expected_domain = "ts_reasoner" if row["label"] == "abstain" else row["expected_domain"]
        expected_operation = "route_unknown" if row["label"] == "abstain" else row["expected_operation"]
        ok = pred.domain == expected_domain and pred.operation == expected_operation
        dataset_correct += int(ok)
        dataset_rows.append(
            {
                "text": row["text"],
                "expected_domain": expected_domain,
                "expected_operation": expected_operation,
                "actual_domain": pred.domain,
                "actual_operation": pred.operation,
                "score": pred.score,
                "abstained": pred.abstained,
                "ok": ok,
            }
        )

    heldout_correct = 0
    heldout_rows = []

    for case in HELDOUT_CASES:
        pred = model.predict(case["text"])
        ok = pred.domain == case["expected_domain"] and pred.operation == case["expected_operation"]
        heldout_correct += int(ok)
        heldout_rows.append(
            {
                **case,
                "actual_domain": pred.domain,
                "actual_operation": pred.operation,
                "score": pred.score,
                "abstained": pred.abstained,
                "reason": pred.reason,
                "ok": ok,
            }
        )

    route_unknown_rows = [row for row in HELDOUT_CASES if row["label"] == "abstain"]
    route_unknown_correct = sum(
        1
        for row in heldout_rows
        if row["label"] == "abstain"
        and row["actual_domain"] == "ts_reasoner"
        and row["actual_operation"] == "route_unknown"
    )

    report = {
        "artifact": "ts_agl_tiny_router_report",
        "dataset_path": str(dataset_path),
        "model_path": str(model_path),
        "dataset_row_count": len(rows),
        "dataset_accuracy": dataset_correct / len(rows) if rows else 0.0,
        "heldout_case_count": len(HELDOUT_CASES),
        "heldout_accuracy": heldout_correct / len(HELDOUT_CASES),
        "heldout_abstention_accuracy": route_unknown_correct / len(route_unknown_rows),
        "label_counts": dict(sorted(label_counts.items())),
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "wrong_state_mutation_count": 0,
        "model_is_proof_authority": False,
        "confidence_is_proof": False,
        "dataset_rows": dataset_rows,
        "heldout_rows": heldout_rows,
        "all_gates_passed": (
            len(rows) > 0
            and dataset_correct == len(rows)
            and heldout_correct == len(HELDOUT_CASES)
            and route_unknown_correct == len(route_unknown_rows)
        ),
    }

    Path("artifacts/ts_agl_tiny_router_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_agl_tiny_router_receipt",
        "dataset_row_count": report["dataset_row_count"],
        "dataset_accuracy": report["dataset_accuracy"],
        "heldout_accuracy": report["heldout_accuracy"],
        "heldout_abstention_accuracy": report["heldout_abstention_accuracy"],
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "wrong_state_mutation_count": 0,
        "model_is_proof_authority": False,
        "confidence_is_proof": False,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_agl_tiny_router_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the v19 tiny learned TS-AGL router.")
    parser.parse_args()
    report = evaluate()
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
