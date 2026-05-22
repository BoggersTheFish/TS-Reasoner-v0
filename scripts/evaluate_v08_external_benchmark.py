#!/usr/bin/env python3
"""Evaluate v0.8 externalized benchmark baselines."""

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


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    coordinator = TensionCoordinator.from_json(COUPLING) if COUPLING.exists() else None
    tasks = load_benchmark(DATA)
    report = BenchmarkRunner(tension_coordinator=coordinator).evaluate(tasks)
    report["benchmark_path"] = str(DATA.relative_to(ROOT))
    report["coupling_matrix"] = str(COUPLING.relative_to(ROOT)) if COUPLING.exists() else None
    report["scope_note"] = (
        "Curated externalized small-reasoning tasks normalized into TS-Reasoner relation form; "
        "not a broad benchmark claim."
    )
    path = ARTIFACTS / "v08_external_benchmark_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

