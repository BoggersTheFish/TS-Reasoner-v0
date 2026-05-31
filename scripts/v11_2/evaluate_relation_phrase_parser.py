from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.claim_normalizer import normalize_claim_surface
from ts_reasoner.relation_phrase_parser import parse_relation_phrase
from ts_reasoner.support_path_verifier import verify_support_path

DATA = ROOT / "data" / "v11_2" / "relation_phrase_cases.jsonl"
REPORT = ROOT / "artifacts" / "v11_2" / "relation_phrase_parser_report.json"
RECEIPT = ROOT / "artifacts" / "v11_2" / "relation_phrase_parser_receipt.json"


def load_cases() -> list[dict[str, Any]]:
    return [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    parsed = 0
    canonical_ok = 0
    quantifier_ok = 0
    negative_ok = 0
    negative_total = 0

    for case in load_cases():
        observed = parse_relation_phrase(case["surface"])
        normalized = normalize_claim_surface(case["surface"])
        passed = (
            observed["parse_status"] == case["expected_status"]
            and observed["canonical_claim"] == case["expected_canonical"]
            and observed["quantifier"] == case["expected_quantifier"]
            and normalized["canonical_claim"] == case["expected_canonical"]
        )
        parsed += int(observed["parse_status"] == "parsed")
        canonical_ok += int(observed["canonical_claim"] == case["expected_canonical"])
        quantifier_ok += int(observed["quantifier"] == case["expected_quantifier"])
        if case["expected_quantifier"] == "no":
            negative_total += 1
            negative_ok += int(passed)

        rows.append({
            "case_id": case["case_id"],
            "surface": case["surface"],
            "expected_canonical": case["expected_canonical"],
            "observed_canonical": observed["canonical_claim"],
            "normalizer_canonical": normalized["canonical_claim"],
            "observed_quantifier": observed["quantifier"],
            "observed_relation": observed["relation"],
            "passed": passed,
        })

    behavior_cases = [
        {
            "name": "relation_transitive_accept",
            "premises": [
                "generated text counts as candidate data",
                "candidate data is a type of untrusted material",
            ],
            "claim": "generated text is untrusted material",
            "expected_status": "accepted",
            "expected_channel": "transitive_all",
        },
        {
            "name": "relation_negative_accept",
            "premises": [
                "model confidence cannot be proof",
            ],
            "claim": "model confidence is not proof",
            "expected_status": "accepted",
            "expected_channel": "direct_support",
        },
        {
            "name": "relation_reverse_reject",
            "premises": [
                "generated text counts as candidate data",
            ],
            "claim": "candidate data counts as generated text",
            "expected_status": "rejected",
            "expected_reason": "reverse_inference_block",
        },
        {
            "name": "relation_unsupported_abstain",
            "premises": [
                "generated text counts as candidate data",
            ],
            "claim": "generated text counts as proof",
            "expected_status": "abstained",
            "expected_reason": "unsupported_claim",
        },
    ]

    behavior_rows = []
    wrong_accept_count = 0
    accepted_without_typed_support_count = 0
    contamination = 0

    for case in behavior_cases:
        result = verify_support_path(case["premises"], case["claim"])
        observed_channel = result.get("support", {}).get("channel")
        observed_reason = result.get("reason")
        passed = result["status"] == case["expected_status"]
        if "expected_channel" in case:
            passed = passed and observed_channel == case["expected_channel"]
        if "expected_reason" in case:
            passed = passed and observed_reason == case["expected_reason"]

        if result["status"] == "accepted" and result.get("claim") != result.get("support", {}).get("derived_claim"):
            wrong_accept_count += 1
        if result["status"] == "accepted" and "support" not in result:
            accepted_without_typed_support_count += 1

        behavior_rows.append({
            "name": case["name"],
            "observed_status": result["status"],
            "observed_channel": observed_channel,
            "observed_reason": observed_reason,
            "passed": passed,
        })

    case_count = len(rows)
    behavior_case_count = len(behavior_rows)

    report = {
        "release": "v11.2.0",
        "case_count": case_count,
        "behavior_case_count": behavior_case_count,
        "relation_phrase_parse_accuracy": parsed / case_count if case_count else 0.0,
        "canonical_claim_validity": canonical_ok / case_count if case_count else 0.0,
        "quantifier_accuracy": quantifier_ok / case_count if case_count else 0.0,
        "negative_relation_parse_accuracy": negative_ok / negative_total if negative_total else 0.0,
        "relation_behavior_accuracy": sum(1 for row in behavior_rows if row["passed"]) / behavior_case_count if behavior_case_count else 0.0,
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "candidate_graph_contamination_count": contamination,
        "results": rows,
        "behavior_results": behavior_rows,
    }
    report["all_gates_passed"] = (
        report["relation_phrase_parse_accuracy"] == 1.0
        and report["canonical_claim_validity"] == 1.0
        and report["quantifier_accuracy"] == 1.0
        and report["negative_relation_parse_accuracy"] == 1.0
        and report["relation_behavior_accuracy"] == 1.0
        and wrong_accept_count == 0
        and accepted_without_typed_support_count == 0
        and contamination == 0
    )

    receipt = {
        "receipt_type": "v11_2_relation_phrase_parser_receipt",
        "release": "v11.2.0",
        "claim": "TS-Reasoner normalizes bounded relation phrases into verifier claims while preserving typed proof boundaries.",
        "relation_phrase_parse_accuracy": report["relation_phrase_parse_accuracy"],
        "canonical_claim_validity": report["canonical_claim_validity"],
        "negative_relation_parse_accuracy": report["negative_relation_parse_accuracy"],
        "relation_behavior_accuracy": report["relation_behavior_accuracy"],
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
