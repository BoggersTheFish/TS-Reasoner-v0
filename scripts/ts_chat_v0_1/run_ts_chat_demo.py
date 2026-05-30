#!/usr/bin/env python3
"""Run TS-Chat v0.1 deterministic demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_chat import demo


REPORT = ROOT / "artifacts/ts_chat_v0_1_demo_receipt.json"


def main() -> int:
    report = demo()

    # Basic gates for the first bounded scratch-chat release.
    report["gates"] = {
        "external_llm_gate": report["external_llm_used"] is False,
        "turn_count_gate": report["turn_count"] == 3,
        "has_receipts_gate": len(report["receipts"]) == 3,
        "rejected_unsupported_requested_claim_gate": any(
            decision["kind"] == "requested_claim" and decision["status"] == "rejected"
            for receipt in report["receipts"]
            for decision in receipt["decisions"]
        ),
        "accepted_supported_question_gate": any(
            decision["kind"] == "question" and decision["status"] == "accepted"
            for receipt in report["receipts"]
            for decision in receipt["decisions"]
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
        "graph_edge_count": report["graph_edge_count"],
        "all_gates_passed": report["gates"]["all_gates_passed"],
        "output": str(REPORT.relative_to(ROOT)),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
