#!/usr/bin/env python3
"""Run TS-Chat v0.5 candidate-language deterministic demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_chat import demo_v0_5_candidate_language_rules


REPORT = ROOT / "artifacts/ts_chat_v0_5_candidate_language_demo_receipt.json"


def main() -> int:
    report = demo_v0_5_candidate_language_rules()

    all_selected_have_rules = all(
        receipt["candidate_selection"]["selected"].get("rule_id")
        for receipt in report["receipts"]
    )

    candidate_counts = [
        len(receipt["candidate_selection"].get("candidates", []))
        for receipt in report["receipts"]
    ]

    report["max_candidate_count"] = max(candidate_counts) if candidate_counts else 0

    report["gates"] = {
        "external_llm_gate": report["external_llm_used"] is False,
        "turn_count_gate": report["turn_count"] == 6,
        "candidate_selection_present_gate": report["has_candidate_selection"] is True,
        "all_selected_have_rules_gate": all_selected_have_rules,
        "multi_candidate_gate": report["max_candidate_count"] >= 2,
        "parse_rule_gate": report["has_parse_rule"] is True,
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
        "selected_rule_count": report["selected_rule_count"],
        "max_candidate_count": report["max_candidate_count"],
        "all_gates_passed": report["gates"]["all_gates_passed"],
        "output": str(REPORT.relative_to(ROOT)),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
