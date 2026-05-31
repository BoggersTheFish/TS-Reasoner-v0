#!/usr/bin/env python3
"""Public demo receipt for TS-Reasoner v7.7.0 provenance trust pressure."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.trust_pressure import run_trust_pressure_demo  # noqa: E402


OUT_DIR = Path("artifacts/trust_pressure/v7_7_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_7_trust_pressure_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_7_trust_pressure_report.json")


def main() -> None:
    receipt = run_trust_pressure_demo(OUT_DIR)
    report = json.loads(Path(receipt["report_path"]).read_text(encoding="utf-8"))

    public_receipt = {
        "schema": "ts_reasoner_v7_7_trust_pressure_public_receipt",
        "release": "v7.7.0",
        "milestone": "Provenance Trust Pressure",
        "external_llm_used": False,
        "out_dir": str(OUT_DIR),
        "source_count": receipt["source_count"],
        "unsafe_pressure_detected": receipt["unsafe_pressure_detected"],
        "unsafe_merge_blocked": receipt["unsafe_merge_blocked"],
        "safe_merge_allowed": receipt["safe_merge_allowed"],
        "post_merge_answer_accepted": receipt["post_merge_answer_accepted"],
        "pack_compare_pressure_record_count": receipt["pack_compare_pressure_record_count"],
        "candidate_graph_contamination_count": receipt["candidate_graph_contamination_count"],
        "trust_is_not_proof": receipt["trust_is_not_proof"],
        "source_weight_is_not_proof": receipt["source_weight_is_not_proof"],
        "trust_pressure_is_not_proof": receipt["trust_pressure_is_not_proof"],
        "pack_merge_is_not_proof": receipt["pack_merge_is_not_proof"],
        "typed_verifier_remains_proof_authority": receipt["typed_verifier_remains_proof_authority"],
        "all_gates_passed": receipt["all_gates_passed"],
        "boundary": receipt["boundary"],
    }

    public_report = {
        "schema": "ts_reasoner_v7_7_trust_pressure_public_report",
        "release": "v7.7.0",
        **report,
    }

    RECEIPT_PATH.write_text(json.dumps(public_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(public_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(public_receipt, indent=2, sort_keys=True))

    if not public_receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
