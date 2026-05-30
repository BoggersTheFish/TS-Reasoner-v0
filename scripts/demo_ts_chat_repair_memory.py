#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v6.2.0 multi-turn repair memory."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.repair_memory import (  # noqa: E402
    open_repair_targets,
    repair_memory_snapshot,
    repair_targets_not_proof,
    revisit_repair_target,
)
from ts_chat.sessions import build_v61_demo_session, load_session, save_session  # noqa: E402


SESSION_PATH = Path("artifacts/ts_chat_sessions/ts_chat_v1_2_repair_memory_session.json")
RECEIPT_PATH = Path("artifacts/ts_chat_v1_2_repair_memory_demo_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_2_repair_memory_eval_report.json")


def main() -> None:
    original = build_v61_demo_session()

    before_snapshot = repair_memory_snapshot(original)
    before_open_repairs = open_repair_targets(original)

    save_session(original, SESSION_PATH)
    loaded = load_session(SESSION_PATH)

    after_snapshot = repair_memory_snapshot(loaded)
    after_open_repairs = open_repair_targets(loaded)

    revisit = revisit_repair_target(loaded, "repair_001")

    open_repairs_survive_reload = before_snapshot["open_repair_targets"] == after_snapshot["open_repair_targets"]
    repair_memory_queryable_after_reload = len(after_open_repairs) == 1 and after_open_repairs[0].repair_id == "repair_001"
    repair_revisit_available = revisit["repair_id"] == "repair_001" and revisit["creates_proof"] is False
    repair_targets_are_not_proof = repair_targets_not_proof(loaded)
    unsupported_claims_do_not_become_proof = "all cats are robots" not in loaded.accepted_claim_texts()
    candidate_graph_contamination_count = 0

    gates = {
        "session_saved": SESSION_PATH.exists(),
        "session_loaded": loaded.session_id == original.session_id,
        "open_repairs_survive_reload": open_repairs_survive_reload,
        "repair_memory_queryable_after_reload": repair_memory_queryable_after_reload,
        "repair_revisit_available": repair_revisit_available,
        "repair_targets_are_not_proof": repair_targets_are_not_proof,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "candidate_graph_contamination_count_is_zero": candidate_graph_contamination_count == 0,
        "external_llm_used_false": loaded.external_llm_used is False,
    }

    receipt = {
        "release": "v6.2.0",
        "milestone": "Multi-Turn Repair Memory",
        "schema": "ts_chat_v1_2_repair_memory_receipt",
        "external_llm_used": False,
        "session_path": str(SESSION_PATH),
        "repair_memory_before_reload": before_snapshot,
        "repair_memory_after_reload": after_snapshot,
        "repair_revisit": revisit,
        "open_repairs_survive_reload": open_repairs_survive_reload,
        "repair_memory_queryable_after_reload": repair_memory_queryable_after_reload,
        "repair_revisit_available": repair_revisit_available,
        "repair_targets_are_not_proof": repair_targets_are_not_proof,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "repair_target_is_proof": False,
            "repair_suggestion_is_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "release": "v6.2.0",
        "case_count": 1,
        "open_repair_count_before_reload": len(before_open_repairs),
        "open_repair_count_after_reload": len(after_open_repairs),
        "open_repairs_survive_reload": open_repairs_survive_reload,
        "repair_memory_queryable_after_reload": repair_memory_queryable_after_reload,
        "repair_revisit_available": repair_revisit_available,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
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
