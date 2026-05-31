from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.gpt2_boundary.procedural_curriculum import CurriculumConfig, build_and_validate

CONFIG = ROOT / "data" / "v11_4" / "procedural_curriculum_config.json"
TASKS_OUT = ROOT / "artifacts" / "v11_4" / "procedural_curriculum.jsonl"
REPORT = ROOT / "artifacts" / "v11_4" / "procedural_curriculum_report.json"
RECEIPT = ROOT / "artifacts" / "v11_4" / "procedural_curriculum_receipt.json"


def main() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    config = CurriculumConfig(**payload)
    built = build_and_validate(config)
    tasks = built["tasks"]
    report = built["report"]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    TASKS_OUT.write_text(
        "\n".join(json.dumps(task, sort_keys=True) for task in tasks) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "receipt_type": "v11_4_procedural_curriculum_receipt",
        "release": "v11.4.0",
        "claim": "TS-Reasoner generates deterministic verifier-first reasoning curricula from templates and graph structures.",
        "task_count": report["task_count"],
        "duplicate_task_rate": report["duplicate_task_rate"],
        "label_validity": report["label_validity"],
        "family_coverage": report["family_coverage"],
        "trap_coverage": report["trap_coverage"],
        "deterministic_rebuild_hash_match": report["deterministic_rebuild_hash_match"],
        "arena_candidate_graph_contamination_count": report["arena_candidate_graph_contamination_count"],
        "arena_accepted_without_typed_support_count": report["arena_accepted_without_typed_support_count"],
        "curriculum_hash": report["curriculum_hash"],
        "all_gates_passed": report["all_gates_passed"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not report["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
