#!/usr/bin/env python3
"""Run TS-Chat v0.4 repair-resolution deterministic demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_chat import demo_v0_4_repair_resolution


REPORT = ROOT / "artifacts/ts_chat_v0_4_repair_resolution_demo_receipt.json"


def main() -> int:
    report = demo_v0_4_repair_resolution()

    resolved_repairs = [
        record["repair_target"]
        for receipt in report["receipts"]
        for record in receipt["records_created"]
        if "repair_target" in record and record["repair_target"]["status"] == "resolved"
    ]

    open_repairs = [
        repair
        for receipt in report["receipts"]
        for repair in receipt["common_ground"].get("repair_targets", [])
        if repair["status"] == "open"
    ]

    report["resolved_repair_count"] = len(resolved_repairs)
    report["open_repair_count_final"] = len(open_repairs)

    report["gates"] = {
        "external_llm_gate": report["external_llm_used"] is False,
        "turn_count_gate": report["turn_count"] == 8,
        "repair_targets_present_gate": report["repair_target_count"] >= 2,
        "resolved_repair_gate": report["resolved_repair_count"] >= 1,
        "parse_repair_still_open_gate": report["open_repair_count_final"] >= 1,
        "repair_resolution_message_gate": any(
            "Resolved repair targets:" in receipt["response"]
            for receipt in report["receipts"]
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
        "resolved_repair_count": report["resolved_repair_count"],
        "open_repair_count_final": report["open_repair_count_final"],
        "all_gates_passed": report["gates"]["all_gates_passed"],
        "output": str(REPORT.relative_to(ROOT)),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
