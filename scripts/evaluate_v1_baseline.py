#!/usr/bin/env python3
"""Generate the TS-Reasoner v1.0 stable trace-contract baseline receipt."""

from __future__ import annotations

import json
import sys
from datetime import date, timezone, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.benchmark import BenchmarkRunner, load_benchmark  # noqa: E402
from ts_reasoner.tension_agents import TensionCoordinator  # noqa: E402


ARTIFACTS = ROOT / "artifacts"
DATA = ROOT / "data" / "external_benchmark_v1.jsonl"
COUPLING = ROOT / "artifacts" / "learned_coupling_matrix_v05.json"
BASELINE_REPORT = ARTIFACTS / "v1_baseline_report.json"
RELEASE_RECEIPT = ARTIFACTS / "release_receipt_v1.0.0.json"


def _status_summary(report: dict) -> dict:
    rows = report["tasks"]
    full_rows = [row["baselines"]["full_control_loop"] for row in rows]
    return {
        "expected_pass_tasks": sum(1 for row in rows if row["expected_status"] == "expected_pass"),
        "known_failure_tasks": sum(1 for row in rows if row["expected_status"] == "known_failure"),
        "full_control_loop_correct": sum(1 for row in full_rows if row["correct"]),
        "full_control_loop_total": len(full_rows),
    }


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    coordinator = TensionCoordinator.from_json(COUPLING) if COUPLING.exists() else None
    tasks = load_benchmark(DATA)
    report = BenchmarkRunner(tension_coordinator=coordinator).evaluate(tasks)
    report["version"] = "v1.0.0"
    report["benchmark_path"] = str(DATA.relative_to(ROOT))
    report["coupling_matrix"] = str(COUPLING.relative_to(ROOT)) if COUPLING.exists() else None
    report["trace_contract"] = "TRACE_SCHEMA.md"
    report["scope_note"] = (
        "v1.0 freezes the public trace contract and benchmark receipt shape. "
        "It is not a larger model or broad reasoning benchmark."
    )
    report["v1_claim"] = (
        "The same TS-Reasoner output schema is stable enough for external inspection, "
        "with benchmark receipts that include expected passes and adversarial known limits."
    )
    report["status_summary"] = _status_summary(report)
    report["remaining_limits"] = [
        "Positive universal all/all chains are the only supported transitive proof-chain family.",
        "Multi-word terms, unless/counterfactual scope, and negative transitive chains remain known limits.",
        "The parser and CIG are heuristic inspection tools, not a formal prover.",
        "TensionProofLM-22M is a target with a smoke receipt, not a trained released checkpoint.",
    ]
    BASELINE_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "version": "v1.0.0",
        "date": date.today().isoformat(),
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim": report["v1_claim"],
        "command": "python3 scripts/evaluate_v1_baseline.py",
        "artifacts": [
            str(BASELINE_REPORT.relative_to(ROOT)),
            "artifacts/tensionlm_bridge_smoke.json",
            "artifacts/tensionprooflm_smoke_report.json",
            "TRACE_SCHEMA.md",
            "BENCHMARKS.md",
            "LIMITATIONS.md",
            "MODEL_CARD.md",
        ],
        "limitations": report["remaining_limits"],
        "additional_receipts": [
            "python3 scripts/run_tensionlm_bridge.py --offline",
            "python3 scripts/run_tensionprooflm_smoke.py",
        ],
        "status_summary": report["status_summary"],
    }
    RELEASE_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
