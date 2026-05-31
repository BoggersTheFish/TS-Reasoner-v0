#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmarks.gpt2_boundary.run_gpt2_small_baseline import run_gpt2_small_baseline
from benchmarks.gpt2_boundary.score_gpt2_outputs import score_gpt2_outputs
from ts_reasoner.typed_support import canonical_hash


TASKS = ROOT / "data" / "v10_8" / "gpt2_boundary_tasks.jsonl"
CONFIG = ROOT / "data" / "v10_9" / "gpt2_small_baseline_config.json"
OUTPUTS = ROOT / "artifacts" / "gpt2_small_baseline_outputs.jsonl"
REPORT = ROOT / "artifacts" / "gpt2_small_baseline_report.json"
RECEIPT = ROOT / "artifacts" / "gpt2_small_baseline_receipt.json"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def main() -> int:
    if not TASKS.exists():
        subprocess.run([sys.executable, "scripts/v10_8/evaluate_gpt2_boundary_task_schema.py"], cwd=ROOT, check=True)
    tasks = load_jsonl(TASKS)
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "model": "gpt2-small",
        "prompt_format": "ANSWER/CLAIM/SUPPORT/STATUS",
        "baseline_source": "frozen_offline_gpt2_small_boundary_fixture",
        "network_required": False,
        "task_file": str(TASKS.relative_to(ROOT)),
    }
    CONFIG.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = run_gpt2_small_baseline(tasks)
    write_jsonl(OUTPUTS, outputs)
    report = score_gpt2_outputs(tasks, outputs)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "release": "v10.9.0",
        "claim": "v10.9 freezes a reproducible GPT-2-small baseline on the TS verifier-first boundary task suite.",
        "config_hash": canonical_hash(config),
        "outputs_hash": canonical_hash(outputs),
        "report_hash": canonical_hash(report),
        "baseline_frozen": report["baseline_frozen"],
        "all_gates_passed": report["task_count"] == 100 and report["baseline_frozen"],
        "metrics": {key: report[key] for key in report if key != "results"},
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
