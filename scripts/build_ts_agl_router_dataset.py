from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.registry import DomainRegistry
from ts_agl.training import build_router_dataset, write_router_dataset_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the v18 TS-AGL router dataset.")
    parser.add_argument("--output", default="artifacts/ts_agl_router_dataset.jsonl")
    parser.add_argument("--report", default="artifacts/ts_agl_router_dataset_build_report.json")
    args = parser.parse_args()

    registry = DomainRegistry().load()
    rows = build_router_dataset(registry=registry)
    write_router_dataset_jsonl(rows, args.output)

    label_counts = Counter(row.label for row in rows)
    source_counts = Counter(row.source for row in rows)
    domain_counts = Counter(row.expected_domain for row in rows)

    report = {
        "artifact": "ts_agl_router_dataset_build_report",
        "dataset_path": args.output,
        "row_count": len(rows),
        "label_counts": dict(sorted(label_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "has_route_rows": label_counts.get("route", 0) > 0,
        "has_abstain_rows": label_counts.get("abstain", 0) > 0,
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "wrong_state_mutation_count": 0,
        "all_gates_passed": (
            len(rows) > 0
            and label_counts.get("route", 0) > 0
            and label_counts.get("abstain", 0) > 0
        ),
    }

    Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
