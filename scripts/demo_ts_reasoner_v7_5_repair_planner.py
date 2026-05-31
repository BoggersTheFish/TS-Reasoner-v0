#!/usr/bin/env python3
"""Public demo receipt for TS-Reasoner v7.5.0 repair planner."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.repair_planner_demo import run_repair_planner_demo  # noqa: E402


OUT_DIR = Path("artifacts/repair_planner/v7_5_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_5_repair_planner_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_5_repair_planner_report.json")


def main() -> None:
    receipt = run_repair_planner_demo(OUT_DIR)
    report = json.loads(Path(receipt["report_path"]).read_text(encoding="utf-8"))

    public_receipt = {
        "schema": "ts_reasoner_v7_5_repair_planner_public_receipt",
        "release": "v7.5.0",
        "milestone": "Repair Planner",
        "external_llm_used": False,
        "out_dir": str(OUT_DIR),
        "missing_support_plan_count": receipt["missing_support_plan_count"],
        "contradiction_plan_count": receipt["contradiction_plan_count"],
        "candidate_graph_contamination_count": receipt["candidate_graph_contamination_count"],
        "repair_plans_are_not_proof": receipt["repair_plans_are_not_proof"],
        "generated_bridge_terms_are_not_proof": receipt["generated_bridge_terms_are_not_proof"],
        "user_confirmation_is_not_proof": receipt["user_confirmation_is_not_proof"],
        "typed_verifier_remains_proof_authority": receipt["typed_verifier_remains_proof_authority"],
        "all_gates_passed": receipt["all_gates_passed"],
        "boundary": receipt["boundary"],
    }

    public_report = {
        "schema": "ts_reasoner_v7_5_repair_planner_public_report",
        "release": "v7.5.0",
        **report,
    }

    RECEIPT_PATH.write_text(json.dumps(public_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(public_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(public_receipt, indent=2, sort_keys=True))

    if not public_receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
