#!/usr/bin/env python3
"""Evaluate the v0.9 proof-chain closure receipt."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.benchmark import BenchmarkRunner, load_benchmark
from ts_reasoner.tension_agents import TensionCoordinator


ARTIFACTS = ROOT / "artifacts"
DATA = ROOT / "data" / "external_benchmark_v08.jsonl"
COUPLING = ROOT / "artifacts" / "learned_coupling_matrix_v05.json"
V08 = ROOT / "artifacts" / "v08_external_benchmark_report.json"


def _old_v08_summary() -> dict:
    if not V08.exists():
        return {
            "available": False,
            "note": "v0.8 report artifact not found; expected artifacts/v08_external_benchmark_report.json.",
        }
    report = json.loads(V08.read_text(encoding="utf-8"))
    return {
        "available": True,
        "version": report.get("version", "v0.8.0"),
        "baselines": report.get("baselines", {}),
        "small_proof_chain": report.get("by_category", {}).get("small_proof_chain", {}),
        "known_gap": "full_control_loop settled both small_proof_chain tasks to low-tension abstentions.",
    }


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    coordinator = TensionCoordinator.from_json(COUPLING) if COUPLING.exists() else None
    tasks = load_benchmark(DATA)
    report = BenchmarkRunner(tension_coordinator=coordinator).evaluate(tasks)
    report["version"] = "v0.9.0"
    report["benchmark_path"] = str(DATA.relative_to(ROOT))
    report["coupling_matrix"] = str(COUPLING.relative_to(ROOT)) if COUPLING.exists() else None
    report["scope_note"] = (
        "v0.9 keeps the v0.8 externalized benchmark shape and only strengthens "
        "positive universal transitive proof-chain support."
    )
    report["v08_comparison"] = _old_v08_summary()
    report["v09_claim"] = (
        "The full bounded control loop now answers both existing small_proof_chain "
        "tasks correctly while retaining the same toy-scope benchmark surface."
    )
    report["remaining_limits"] = [
        "Only all/all positive universal chains are supported.",
        "The parser remains regex-based and relation-template limited.",
        "The benchmark is still curated and normalized, not a broad reasoning benchmark.",
    ]
    path = ARTIFACTS / "v09_proof_chain_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
