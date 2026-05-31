from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.paragraph_decomposer import decompose_paragraph
from ts_reasoner.support_path_verifier import verify_support_path

DATA = ROOT / "data" / "v11_3" / "paragraph_reasoning_cases.jsonl"
REPORT = ROOT / "artifacts" / "v11_3" / "paragraph_decomposer_report.json"
RECEIPT = ROOT / "artifacts" / "v11_3" / "paragraph_decomposer_receipt.json"


def load_cases() -> list[dict[str, Any]]:
    return [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    premise_ok = 0
    claim_ok = 0
    status_ok = 0
    verifier_ok = 0
    safe_abstain = 0
    safe_abstain_total = 0
    wrong_accept_count = 0
    accepted_without_typed_support_count = 0
    contamination = 0

    for case in load_cases():
        observed = decompose_paragraph(case["paragraph"])
        expected_premises = case["expected_premises"]
        expected_claim = case["expected_claim"]

        premise_passed = observed["premises"] == expected_premises
        claim_passed = observed["candidate_claim"] == expected_claim
        status_passed = observed["status"] == case["expected_status"]

        premise_ok += int(premise_passed)
        claim_ok += int(claim_passed)
        status_ok += int(status_passed)

        if case["expected_status"] == "abstained":
            safe_abstain_total += 1
            safe_abstain += int(observed["status"] == "abstained" and not observed["candidate_claim"])
            verifier_result = {"status": "abstained", "reason": observed["reason"], "claim": observed["candidate_claim"]}
        else:
            verifier_result = verify_support_path(observed["premises"], observed["candidate_claim"])

        verifier_passed = verifier_result["status"] == case["expected_verifier_status"]
        if "expected_channel" in case:
            verifier_passed = verifier_passed and verifier_result.get("support", {}).get("channel") == case["expected_channel"]
        if "expected_reason" in case:
            verifier_passed = verifier_passed and verifier_result.get("reason") == case["expected_reason"]

        verifier_ok += int(verifier_passed)

        if verifier_result["status"] == "accepted" and verifier_result.get("claim") != verifier_result.get("support", {}).get("derived_claim"):
            wrong_accept_count += 1
        if verifier_result["status"] == "accepted" and "support" not in verifier_result:
            accepted_without_typed_support_count += 1

        rows.append({
            "case_id": case["case_id"],
            "observed_status": observed["status"],
            "observed_premises": observed["premises"],
            "observed_claim": observed["candidate_claim"],
            "observed_verifier_status": verifier_result["status"],
            "observed_channel": verifier_result.get("support", {}).get("channel"),
            "observed_reason": verifier_result.get("reason"),
            "premise_passed": premise_passed,
            "claim_passed": claim_passed,
            "status_passed": status_passed,
            "verifier_passed": verifier_passed,
        })

    case_count = len(rows)
    report = {
        "release": "v11.3.0",
        "case_count": case_count,
        "premise_extraction_accuracy": premise_ok / case_count if case_count else 0.0,
        "target_claim_extraction_accuracy": claim_ok / case_count if case_count else 0.0,
        "decomposition_status_accuracy": status_ok / case_count if case_count else 0.0,
        "verifier_behavior_accuracy": verifier_ok / case_count if case_count else 0.0,
        "safe_abstain_on_ambiguous_input": safe_abstain / safe_abstain_total if safe_abstain_total else 1.0,
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "candidate_graph_contamination_count": contamination,
        "results": rows,
    }
    report["all_gates_passed"] = (
        report["premise_extraction_accuracy"] == 1.0
        and report["target_claim_extraction_accuracy"] == 1.0
        and report["decomposition_status_accuracy"] == 1.0
        and report["verifier_behavior_accuracy"] == 1.0
        and report["safe_abstain_on_ambiguous_input"] == 1.0
        and wrong_accept_count == 0
        and accepted_without_typed_support_count == 0
        and contamination == 0
    )

    receipt = {
        "receipt_type": "v11_3_paragraph_decomposer_receipt",
        "release": "v11.3.0",
        "claim": "TS-Reasoner decomposes bounded natural-language paragraphs into verifier premises and target claims while preserving abstention and typed proof boundaries.",
        "premise_extraction_accuracy": report["premise_extraction_accuracy"],
        "target_claim_extraction_accuracy": report["target_claim_extraction_accuracy"],
        "verifier_behavior_accuracy": report["verifier_behavior_accuracy"],
        "safe_abstain_on_ambiguous_input": report["safe_abstain_on_ambiguous_input"],
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "candidate_graph_contamination_count": contamination,
        "all_gates_passed": report["all_gates_passed"],
    }

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not report["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
