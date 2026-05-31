#!/usr/bin/env python3
"""Public demo receipt for TS-Reasoner v7.8.0 proof / repair search."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.proof_repair_search import run_proof_repair_search_demo  # noqa: E402


OUT_DIR = Path("artifacts/proof_repair_search/v7_8_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_8_proof_repair_search_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_8_proof_repair_search_report.json")


def main() -> None:
    receipt = run_proof_repair_search_demo(OUT_DIR)
    report = json.loads(Path(receipt["report_path"]).read_text(encoding="utf-8"))

    public_receipt = {
        "schema": "ts_reasoner_v7_8_proof_repair_search_public_receipt",
        "release": "v7.8.0",
        "milestone": "Minimal Proof / Repair Search",
        "external_llm_used": False,
        "out_dir": str(OUT_DIR),
        "prove_support_path_length": receipt["prove_support_path_length"],
        "missing_status_after_repair": receipt["missing_status_after_repair"],
        "cut_suggestion_count": receipt["cut_suggestion_count"],
        "candidate_graph_contamination_count": receipt["candidate_graph_contamination_count"],
        "search_results_are_not_proof": receipt["search_results_are_not_proof"],
        "missing_suggestions_are_not_proof": receipt["missing_suggestions_are_not_proof"],
        "cut_suggestions_are_not_proof": receipt["cut_suggestions_are_not_proof"],
        "typed_verifier_remains_proof_authority": receipt["typed_verifier_remains_proof_authority"],
        "all_gates_passed": receipt["all_gates_passed"],
        "boundary": receipt["boundary"],
    }

    public_report = {
        "schema": "ts_reasoner_v7_8_proof_repair_search_public_report",
        "release": "v7.8.0",
        **report,
    }

    RECEIPT_PATH.write_text(json.dumps(public_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(public_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(public_receipt, indent=2, sort_keys=True))

    if not public_receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
