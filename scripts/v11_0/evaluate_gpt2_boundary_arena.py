#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmarks.gpt2_boundary.compare_ts_vs_gpt2 import compare_ts_vs_gpt2
from benchmarks.gpt2_boundary.run_gpt2_small_baseline import run_gpt2_small_baseline
from benchmarks.gpt2_boundary.run_ts_reasoner_arena import run_ts_reasoner_arena
from ts_reasoner.typed_support import canonical_hash


TASKS = ROOT / "data" / "v10_8" / "gpt2_boundary_tasks.jsonl"
GPT2_OUTPUTS = ROOT / "artifacts" / "gpt2_small_baseline_outputs.jsonl"
TS_OUTPUTS = ROOT / "artifacts" / "ts_reasoner_gpt2_boundary_outputs.jsonl"
REPORT = ROOT / "artifacts" / "ts_reasoner_vs_gpt2_boundary_report.json"
RECEIPT = ROOT / "artifacts" / "v11_0_gpt2_boundary_arena_receipt.json"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def main() -> int:
    if not TASKS.exists():
        subprocess.run([sys.executable, "scripts/v10_8/evaluate_gpt2_boundary_task_schema.py"], cwd=ROOT, check=True)
    if not GPT2_OUTPUTS.exists():
        subprocess.run([sys.executable, "scripts/v10_9/evaluate_gpt2_small_baseline.py"], cwd=ROOT, check=True)

    tasks = load_jsonl(TASKS)
    gpt2_outputs = load_jsonl(GPT2_OUTPUTS)
    if len(gpt2_outputs) != len(tasks):
        gpt2_outputs = run_gpt2_small_baseline(tasks)
        write_jsonl(GPT2_OUTPUTS, gpt2_outputs)

    ts_outputs = run_ts_reasoner_arena(tasks)
    write_jsonl(TS_OUTPUTS, ts_outputs)
    report = compare_ts_vs_gpt2(tasks, gpt2_outputs, ts_outputs)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        **report,
        "report_hash": canonical_hash(report),
        "task_file_hash": canonical_hash(tasks),
        "gpt2_outputs_hash": canonical_hash(gpt2_outputs),
        "ts_outputs_hash": canonical_hash(ts_outputs),
        "boundary": {
            "broad_chatbot_victory_claim": False,
            "full_language_model_replacement_claim": False,
            "verifier_first_reasoning_boundary_result": True,
            "gpt2_generates_ts_verifies": True,
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
