#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.typed_support import canonical_hash, evaluate_typed_support_cases, make_typed_support


DATA = ROOT / "data" / "v10_6" / "typed_support_cases.jsonl"
REPORT = ROOT / "artifacts" / "typed_support_objects_report.json"
RECEIPT = ROOT / "artifacts" / "typed_support_objects_receipt.json"


def build_cases() -> list[dict]:
    cases = []
    for idx in range(1, 6):
        claim = f"all A{idx} are C{idx}"
        support = make_typed_support(
            channel="transitive_all",
            premises=[f"all A{idx} are B{idx}", f"all B{idx} are C{idx}"],
            derived_claim=claim,
        )
        cases.append({"case_id": f"typed_valid_{idx:03d}", "case_type": "valid_support", "claim": claim, "support": support, "expected_accept": True})
        fake = dict(support)
        fake["trace_hash"] = "fake"
        cases.append({"case_id": f"typed_fake_{idx:03d}", "case_type": "fake_support", "claim": claim, "support": fake, "expected_accept": False})
        cases.append({"case_id": f"typed_mismatch_{idx:03d}", "case_type": "mismatched_claim", "claim": f"all A{idx} are D{idx}", "support": support, "expected_accept": False})
        cases.append({"case_id": f"typed_empty_{idx:03d}", "case_type": "empty_support", "claim": claim, "support": [], "expected_accept": False})
    return cases


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    cases = build_cases()
    write_jsonl(DATA, cases)
    report = evaluate_typed_support_cases(load_jsonl(DATA))
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "release": "v10.6.0",
        "claim": "v10.6 replaces symbolic support strings with typed, hash-checked verifier support objects.",
        "report_hash": canonical_hash(report),
        "all_gates_passed": report["all_gates_passed"],
        "metrics": {key: report[key] for key in report if key != "results"},
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
