#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v7.3.0 branching worlds."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.branching_worlds import run_branching_worlds_demo  # noqa: E402


OUT_DIR = Path("artifacts/branching_worlds/v7_3_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_3_branching_worlds_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_3_branching_worlds_report.json")


def main() -> None:
    receipt = run_branching_worlds_demo(OUT_DIR)
    report = json.loads(Path(receipt["report_path"]).read_text(encoding="utf-8"))

    public_receipt = {
        "schema": "ts_reasoner_v7_3_branching_worlds_public_receipt",
        "release": "v7.3.0",
        "milestone": "Branching Worlds",
        "external_llm_used": False,
        "out_dir": str(OUT_DIR),
        "branch_count": receipt["branch_count"],
        "branch_names": receipt["branch_names"],
        "unsafe_merge_blocked": report["unsafe_merge_blocked"],
        "safe_merge_allowed": report["safe_merge_allowed"],
        "safe_merge_added_edges": report["safe_merge_added_edges"],
        "safe_merge_resolved_repair": report["safe_merge_resolved_repair"],
        "post_merge_answer_accepted": report["post_merge_answer_accepted"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "branching_worlds_are_not_proof": receipt["branching_worlds_are_not_proof"],
        "merge_is_not_proof": receipt["merge_is_not_proof"],
        "typed_verifier_remains_proof_authority": receipt["typed_verifier_remains_proof_authority"],
        "all_gates_passed": receipt["all_gates_passed"],
        "boundary": receipt["boundary"],
    }

    public_report = {
        "schema": "ts_reasoner_v7_3_branching_worlds_public_report",
        "release": "v7.3.0",
        **report,
    }

    RECEIPT_PATH.write_text(json.dumps(public_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(public_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(public_receipt, indent=2, sort_keys=True))

    if not public_receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
