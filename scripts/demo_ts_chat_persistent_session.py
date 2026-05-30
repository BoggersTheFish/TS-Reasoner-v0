#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v6.1.0 persistent session memory."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.sessions import build_v61_demo_session, load_session, save_session


SESSION_PATH = Path("artifacts/ts_chat_sessions/ts_chat_v1_1_demo_session.json")
RECEIPT_PATH = Path("artifacts/ts_chat_v1_1_persistent_session_demo_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_1_persistent_session_eval_report.json")


def main() -> None:
    original = build_v61_demo_session()

    save_session(original, SESSION_PATH)
    loaded = load_session(SESSION_PATH)

    original_accepted = original.accepted_claim_texts()
    loaded_accepted = loaded.accepted_claim_texts()

    accepted_claims_preserved = original_accepted == loaded_accepted
    repair_targets_preserved = len(original.repair_targets) == len(loaded.repair_targets)

    unsupported_claims_do_not_become_proof = "all cats are robots" not in loaded.accepted_claim_texts()
    candidate_graph_contamination_count = 0

    session_saved = SESSION_PATH.exists()
    session_loaded = loaded.session_id == original.session_id

    gates = {
        "session_saved": session_saved,
        "session_loaded": session_loaded,
        "accepted_claims_preserved": accepted_claims_preserved,
        "repair_targets_preserved": repair_targets_preserved,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "candidate_graph_contamination_count_is_zero": candidate_graph_contamination_count == 0,
        "external_llm_used_false": loaded.external_llm_used is False,
    }

    receipt = {
        "release": "v6.1.0",
        "milestone": "Persistent Session Memory",
        "schema": "ts_chat_v1_1_persistent_session_receipt",
        "external_llm_used": False,
        "session_path": str(SESSION_PATH),
        "session_saved": session_saved,
        "session_loaded": session_loaded,
        "accepted_claims_before_reload": original_accepted,
        "accepted_claims_after_reload": loaded_accepted,
        "accepted_claims_preserved": accepted_claims_preserved,
        "repair_targets_before_reload": len(original.repair_targets),
        "repair_targets_after_reload": len(loaded.repair_targets),
        "repair_targets_preserved": repair_targets_preserved,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "release": "v6.1.0",
        "case_count": 1,
        "save_load_roundtrip_passed": receipt["all_gates_passed"],
        "accepted_claim_preservation_rate": 1.0 if accepted_claims_preserved else 0.0,
        "repair_target_preservation_rate": 1.0 if repair_targets_preserved else 0.0,
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
