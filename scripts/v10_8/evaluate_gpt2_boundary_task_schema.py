#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmarks.gpt2_boundary.build_abstention_tasks import build_fluent_unsupported_tasks, build_irrelevant_confidence_tasks, build_unsupported_claim_tasks
from benchmarks.gpt2_boundary.build_contradiction_tasks import build_contradiction_tasks, build_messy_wrapper_tasks, build_reverse_inference_tasks
from benchmarks.gpt2_boundary.build_logic_tasks import build_direct_support_tasks, build_negative_exclusion_tasks, build_three_hop_transitive_tasks, build_two_hop_transitive_tasks
from benchmarks.gpt2_boundary.task_schema import evaluate_task_schema
from ts_reasoner.typed_support import canonical_hash


DATA = ROOT / "data" / "v10_8" / "gpt2_boundary_tasks.jsonl"
REPORT = ROOT / "artifacts" / "gpt2_boundary_task_schema_report.json"
RECEIPT = ROOT / "artifacts" / "gpt2_boundary_task_schema_receipt.json"


def build_tasks() -> list[dict]:
    tasks = []
    tasks.extend(build_direct_support_tasks())
    tasks.extend(build_two_hop_transitive_tasks())
    tasks.extend(build_three_hop_transitive_tasks())
    tasks.extend(build_negative_exclusion_tasks())
    tasks.extend(build_reverse_inference_tasks())
    tasks.extend(build_unsupported_claim_tasks())
    tasks.extend(build_contradiction_tasks())
    tasks.extend(build_messy_wrapper_tasks())
    tasks.extend(build_irrelevant_confidence_tasks())
    tasks.extend(build_fluent_unsupported_tasks())
    return tasks


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    write_jsonl(DATA, build_tasks())
    report = evaluate_task_schema(load_jsonl(DATA))
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "release": "v10.8.0",
        "claim": "v10.8 introduces a frozen GPT-2 boundary task format for comparing raw language completion against verifier-first reasoning.",
        "report_hash": canonical_hash(report),
        "all_gates_passed": report["all_gates_passed"],
        "metrics": {key: report[key] for key in report if key != "results"},
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
