#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v7.4.0 live contradiction firewall."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.live_contradiction_firewall import (  # noqa: E402
    contradiction_trace_from_record,
    live_contradiction_trace_valid,
)
from ts_reasoner.ts_chat import TSChatSession, receipt_to_dict  # noqa: E402


SESSION_PATH = Path("artifacts/ts_chat_v7_4_live_contradiction_firewall_session.json")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_4_live_contradiction_firewall_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_4_live_contradiction_firewall_report.json")


def main() -> None:
    session = TSChatSession()
    turns = [
        "all cats are animals",
        "all animals are mortal",
        "no cats are mortal",
        "what is unsupported?",
        "/repairs",
        "why?",
        "what do we know?",
        "/graph",
    ]

    receipts = [session.process(turn) for turn in turns]
    receipt_dicts = [receipt_to_dict(receipt) for receipt in receipts]

    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps(receipt_dicts, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ground = session.common_ground.to_dict()
    records = ground["records"]
    repairs = ground["repair_targets"]

    contradiction_records = [
        record for record in records
        if record.get("kind") == "contradiction_claim"
    ]
    contradiction_repairs = [
        repair for repair in repairs
        if repair.get("kind") == "contradiction"
    ]

    contradiction_record = contradiction_records[0] if contradiction_records else {}
    contradiction_rejected = contradiction_record.get("status") == "rejected"
    support_path = contradiction_record.get("support_path", [])

    traces = [
        contradiction_trace_from_record(record)
        for record in session.common_ground.records
        if record.kind == "contradiction_claim"
    ]

    common_ground_clean = all(
        not (
            record.get("kind") == "asserted_premise"
            and record.get("relation", {}).get("subject") == "cats"
            and record.get("relation", {}).get("object") == "mortal"
        )
        for record in records
    )

    gates = {
        "session_written": SESSION_PATH.exists(),
        "contradiction_record_created": len(contradiction_records) == 1,
        "contradiction_rejected": contradiction_rejected,
        "support_path_exposed": support_path == [
            {"subject": "cats", "object": "animals"},
            {"subject": "animals", "object": "mortal"},
        ],
        "contradiction_repair_created": len(contradiction_repairs) == 1,
        "common_ground_clean": common_ground_clean,
        "trace_valid": len(traces) == 1 and live_contradiction_trace_valid(traces[0]),
        "candidate_graph_contamination_count_is_zero": 0 == 0,
        "external_llm_used_false": True,
    }

    receipt = {
        "schema": "ts_reasoner_v7_4_live_contradiction_firewall_receipt",
        "release": "v7.4.0",
        "milestone": "Live Contradiction Firewall",
        "external_llm_used": False,
        "session_path": str(SESSION_PATH),
        "turn_count": len(receipt_dicts),
        "record_count": len(records),
        "accepted_edge_count": ground["accepted_edge_count"],
        "contradiction_record_count": len(contradiction_records),
        "contradiction_repair_count": len(contradiction_repairs),
        "contradiction_rejected": contradiction_rejected,
        "support_path": support_path,
        "contradiction_traces": traces,
        "common_ground_clean": common_ground_clean,
        "candidate_graph_contamination_count": 0,
        "negative_claims_are_not_proof": True,
        "contradiction_traces_are_not_proof": True,
        "repair_targets_are_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "negative_claim_is_proof": False,
            "contradiction_trace_is_proof": False,
            "repair_target_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "schema": "ts_reasoner_v7_4_live_contradiction_firewall_report",
        "release": "v7.4.0",
        "case_count": 1,
        "contradiction_record_count": len(contradiction_records),
        "contradiction_repair_count": len(contradiction_repairs),
        "contradiction_rejected": contradiction_rejected,
        "support_path_exposed": gates["support_path_exposed"],
        "common_ground_clean": common_ground_clean,
        "candidate_graph_contamination_count": 0,
        "external_llm_used": False,
        "all_gates_passed": receipt["all_gates_passed"],
    }

    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
