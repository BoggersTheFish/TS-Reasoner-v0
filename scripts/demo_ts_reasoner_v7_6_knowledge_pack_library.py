#!/usr/bin/env python3
"""Public demo receipt for TS-Reasoner v7.6.0 knowledge pack library."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.knowledge_pack_library import run_knowledge_pack_library_demo  # noqa: E402


OUT_DIR = Path("artifacts/knowledge_pack_library/v7_6_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_6_knowledge_pack_library_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_6_knowledge_pack_library_report.json")


def main() -> None:
    receipt = run_knowledge_pack_library_demo(OUT_DIR)
    report = json.loads(Path(receipt["report_path"]).read_text(encoding="utf-8"))

    public_receipt = {
        "schema": "ts_reasoner_v7_6_knowledge_pack_library_public_receipt",
        "release": "v7.6.0",
        "milestone": "Knowledge Pack Library + Safe Merge",
        "external_llm_used": False,
        "out_dir": str(OUT_DIR),
        "pack_count": receipt["pack_count"],
        "unsafe_merge_blocked": receipt["unsafe_merge_blocked"],
        "safe_merge_allowed": receipt["safe_merge_allowed"],
        "safe_merge_added_edges": receipt["safe_merge_added_edges"],
        "post_merge_answer_accepted": receipt["post_merge_answer_accepted"],
        "candidate_graph_contamination_count": receipt["candidate_graph_contamination_count"],
        "pack_import_is_not_proof": receipt["pack_import_is_not_proof"],
        "pack_merge_is_not_proof": receipt["pack_merge_is_not_proof"],
        "pack_metadata_is_not_proof": receipt["pack_metadata_is_not_proof"],
        "typed_verifier_remains_proof_authority": receipt["typed_verifier_remains_proof_authority"],
        "all_gates_passed": receipt["all_gates_passed"],
        "boundary": receipt["boundary"],
    }

    public_report = {
        "schema": "ts_reasoner_v7_6_knowledge_pack_library_public_report",
        "release": "v7.6.0",
        **report,
    }

    RECEIPT_PATH.write_text(json.dumps(public_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(public_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(public_receipt, indent=2, sort_keys=True))

    if not public_receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
