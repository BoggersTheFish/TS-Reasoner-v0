#!/usr/bin/env python3
"""Run TS-Chat v0.3 repair-target deterministic demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_chat import demo_v0_3_repair_targets


REPORT = ROOT / "artifacts/ts_chat_v0_3_repair_targets_demo_receipt.json"


def main() -> int:
    report = demo_v0_3_repair_targets()

    report["gates"] = {
        "external_llm_gate": report["external_llm_used"] is False,
        "turn_count_gate": report["turn_count"] == 7,
        "common_ground_records_gate": report["record_count"] >= 4,
        "repair_targets_present_gate": report["repair_target_count"] >= 2,
        "repairs_command_gate": report["has_repairs_command"] is True,
        "unsupported_repair_gate": any(
            "repair_target" in record
            and record["repair_target"]["kind"] == "missing_support"
            for receipt in report["receipts"]
            for record in receipt["records_created"]
        ),
        "parse_repair_gate": any(
            "repair_target" in record
            and record["repair_target"]["kind"] == "parse_failure"
            for receipt in report["receipts"]
            for record in receipt["records_created"]
        ),
    }
    report["gates"]["all_gates_passed"] = all(report["gates"].values())

    if not report["gates"]["all_gates_passed"]:
        print(json.dumps(report["gates"], indent=2, sort_keys=True))
        return 1

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "version": report["version"],
        "external_llm_used": report["external_llm_used"],
        "turn_count": report["turn_count"],
        "record_count": report["record_count"],
        "repair_target_count": report["repair_target_count"],
        "all_gates_passed": report["gates"]["all_gates_passed"],
        "output": str(REPORT.relative_to(ROOT)),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
