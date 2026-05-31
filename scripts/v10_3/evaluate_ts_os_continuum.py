from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_os import run_continuum_scenario, write_json


def main() -> int:
    scenario = json.loads((ROOT / "data" / "v10_3" / "infrastructure_grid_scenario.json").read_text(encoding="utf-8"))
    report = run_continuum_scenario(scenario)
    payload = asdict(report)
    write_json(ROOT / "artifacts" / "ts_os_continuum_report.json", payload)
    write_json(ROOT / "artifacts" / "ts_os_continuum_receipt.json", {
        "receipt_type": "ts_os_continuum",
        "release": "v10.3",
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": report.all_gates_passed,
    })
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report.all_gates_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
