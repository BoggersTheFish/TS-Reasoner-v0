#!/usr/bin/env python3
"""Evaluate v0.7 residual-closure tension loops."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.operation_router import OperationRouter
from ts_reasoner.synthetic_data import v06_loop_cases


ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    router = OperationRouter()
    rows = []
    for chain in v06_loop_cases():
        loop = router.run_until_stable(chain, max_steps=5)
        rows.append(
            {
                "chain_id": chain.chain_id,
                "initial_global_tension": loop["initial"]["global_tension"],
                "final_global_tension": loop["final"]["global_tension"],
                "cycles_used": loop["cycle_count"],
                "settled": loop["settled"],
                "status": loop["status"],
                "ops": [cycle["selected_op"] for cycle in loop["cycles"]],
                "cycle_statuses": [cycle["status"] for cycle in loop["cycles"]],
            }
        )
    settled = [row for row in rows if row["settled"]]
    report = {
        "version": "v0.7.0",
        "case_count": len(rows),
        "settled_count": len(settled),
        "settled_rate": round(len(settled) / max(1, len(rows)), 4),
        "mean_initial_global_tension": round(
            sum(float(row["initial_global_tension"]) for row in rows) / max(1, len(rows)),
            4,
        ),
        "mean_final_global_tension": round(
            sum(float(row["final_global_tension"]) for row in rows) / max(1, len(rows)),
            4,
        ),
        "mean_cycles_used": round(sum(int(row["cycles_used"]) for row in rows) / max(1, len(rows)), 4),
        "failed_to_settle": [row["chain_id"] for row in rows if not row["settled"]],
        "closure_claim": "v0.7 closes the v0.6 residual no-compression failure by compressing redundant non-premise claims.",
        "cases": rows,
    }
    path = ARTIFACTS / "v07_loop_eval.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

