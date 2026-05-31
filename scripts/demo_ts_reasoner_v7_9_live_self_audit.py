#!/usr/bin/env python3
"""Public demo receipt for TS-Reasoner v7.9.0 live self-audit mode."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.self_audit import run_self_audit_demo  # noqa: E402


OUT_DIR = Path("artifacts/self_audit/v7_9_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_9_live_self_audit_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_9_live_self_audit_report.json")


def main() -> None:
    receipt = run_self_audit_demo(OUT_DIR)
    report = json.loads(Path(receipt["report_path"]).read_text(encoding="utf-8"))

    public_receipt = {
        "schema": "ts_reasoner_v7_9_live_self_audit_public_receipt",
        "release": "v7.9.0",
        "milestone": "Live Self-Audit Mode",
        "external_llm_used": False,
        "out_dir": str(OUT_DIR),
        "record_count": receipt["record_count"],
        "accepted_edge_count": receipt["accepted_edge_count"],
        "rejected_record_count": receipt["rejected_record_count"],
        "contradiction_claim_count": receipt["contradiction_claim_count"],
        "open_repair_count": receipt["open_repair_count"],
        "resolved_repair_count": receipt["resolved_repair_count"],
        "wrong_accept_count": receipt["wrong_accept_count"],
        "unsupported_promotion_count": receipt["unsupported_promotion_count"],
        "candidate_graph_contamination_count": receipt["candidate_graph_contamination_count"],
        "proof_boundary_preserved": receipt["proof_boundary_preserved"],
        "audit_output_is_not_proof": receipt["audit_output_is_not_proof"],
        "audit_metrics_are_not_proof": receipt["audit_metrics_are_not_proof"],
        "risk_scores_are_not_proof": receipt["risk_scores_are_not_proof"],
        "typed_verifier_remains_proof_authority": receipt["typed_verifier_remains_proof_authority"],
        "all_gates_passed": receipt["all_gates_passed"],
        "boundary": receipt["boundary"],
    }

    public_report = {
        "schema": "ts_reasoner_v7_9_live_self_audit_public_report",
        "release": "v7.9.0",
        **report,
    }

    RECEIPT_PATH.write_text(json.dumps(public_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(public_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(public_receipt, indent=2, sort_keys=True))

    if not public_receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
