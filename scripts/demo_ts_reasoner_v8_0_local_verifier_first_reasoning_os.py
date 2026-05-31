#!/usr/bin/env python3
"""Public demo receipt for TS-Reasoner v8.0.0 local verifier-first reasoning OS."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.v8_milestone import run_v8_milestone  # noqa: E402


OUT_DIR = Path("artifacts/v8_milestone/v8_0_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v8_0_local_verifier_first_reasoning_os_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v8_0_local_verifier_first_reasoning_os_report.json")


def main() -> None:
    receipt = run_v8_milestone(OUT_DIR)
    report = json.loads(Path(receipt["report_path"]).read_text(encoding="utf-8"))

    public_receipt = {
        "schema": "ts_reasoner_v8_0_local_verifier_first_reasoning_os_public_receipt",
        "release": "v8.0.0",
        "milestone": "Local Verifier-First Reasoning OS",
        "external_llm_used": receipt["external_llm_used"],
        "out_dir": str(OUT_DIR),
        "component_count": receipt["component_count"],
        "component_gate_pass_count": receipt["component_gate_pass_count"],
        "boundary_ok_count": receipt["boundary_ok_count"],
        "capabilities": receipt["capabilities"],
        "missing_asset_count": len(receipt["missing_assets"]),
        "failed_component_count": len(receipt["failed_components"]),
        "candidate_graph_contamination_count": receipt["candidate_graph_contamination_count"],
        "local_runtime_included": receipt["local_runtime_included"],
        "session_compiler_included": receipt["session_compiler_included"],
        "self_curriculum_included": receipt["self_curriculum_included"],
        "branching_worlds_included": receipt["branching_worlds_included"],
        "live_contradiction_firewall_included": receipt["live_contradiction_firewall_included"],
        "repair_planner_included": receipt["repair_planner_included"],
        "knowledge_pack_library_included": receipt["knowledge_pack_library_included"],
        "trust_pressure_included": receipt["trust_pressure_included"],
        "proof_repair_search_included": receipt["proof_repair_search_included"],
        "live_self_audit_included": receipt["live_self_audit_included"],
        "generated_text_is_not_proof": receipt["generated_text_is_not_proof"],
        "trust_is_not_proof": receipt["trust_is_not_proof"],
        "audit_output_is_not_proof": receipt["audit_output_is_not_proof"],
        "search_results_are_not_proof": receipt["search_results_are_not_proof"],
        "milestone_pack_is_not_external_benchmark_claim": receipt["milestone_pack_is_not_external_benchmark_claim"],
        "typed_verifier_remains_proof_authority": receipt["typed_verifier_remains_proof_authority"],
        "all_gates_passed": receipt["all_gates_passed"],
        "boundary": receipt["boundary"],
    }

    public_report = {
        "schema": "ts_reasoner_v8_0_local_verifier_first_reasoning_os_public_report",
        "release": "v8.0.0",
        **report,
    }

    RECEIPT_PATH.write_text(json.dumps(public_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(public_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(public_receipt, indent=2, sort_keys=True))

    if not public_receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
