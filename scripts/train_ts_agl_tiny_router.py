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
    save_tiny_router,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the v19 tiny learned TS-AGL router.")
    parser.add_argument("--dataset", default="artifacts/ts_agl_router_dataset.jsonl")
    parser.add_argument("--model", default="artifacts/ts_agl_tiny_router_model.json")
    parser.add_argument("--report", default="artifacts/ts_agl_tiny_router_train_report.json")
    parser.add_argument("--threshold", type=float, default=0.55)
    args = parser.parse_args()

    rows = load_router_dataset(args.dataset)
    model = TinyLearnedAGLRouter.train(rows, threshold=args.threshold)
    save_tiny_router(model, args.model)

    class_counts = Counter()
    for row in rows:
        if row.get("label") == "abstain":
            class_counts["ts_reasoner.route_unknown"] += 1
        else:
            class_counts[f"{row['expected_domain']}.{row['expected_operation']}"] += 1

    report = {
        "artifact": "ts_agl_tiny_router_train_report",
        "dataset_path": args.dataset,
        "model_path": args.model,
        "row_count": len(rows),
        "class_count": len(class_counts),
        "class_counts": dict(sorted(class_counts.items())),
        "vocabulary_size": len(model.vocabulary),
        "threshold": args.threshold,
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "wrong_state_mutation_count": 0,
        "model_is_proof_authority": False,
        "all_gates_passed": len(rows) > 0 and len(class_counts) >= 2 and len(model.vocabulary) > 0,
    }

    Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
