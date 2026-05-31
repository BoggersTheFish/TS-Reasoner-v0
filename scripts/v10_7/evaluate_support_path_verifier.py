#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.support_path_verifier import evaluate_support_path_cases
from ts_reasoner.typed_support import canonical_hash


DATA = ROOT / "data" / "v10_7" / "support_path_cases.jsonl"
REPORT = ROOT / "artifacts" / "support_path_verifier_report.json"
RECEIPT = ROOT / "artifacts" / "support_path_verifier_receipt.json"


def build_cases() -> list[dict]:
    cases = []
    for idx in range(1, 9):
        cases.append({"case_id": f"path_direct_{idx:03d}", "premises": [f"all A{idx} are B{idx}"], "claim": f"all A{idx} are B{idx}", "expected_status": "accepted", "expected_channel": "direct_support"})
        cases.append({"case_id": f"path_transitive_{idx:03d}", "premises": [f"all A{idx} are B{idx}", f"all B{idx} are C{idx}"], "claim": f"all A{idx} are C{idx}", "expected_status": "accepted", "expected_channel": "transitive_all"})
        cases.append({"case_id": f"path_negative_{idx:03d}", "premises": [f"all A{idx} are B{idx}", f"no B{idx} are C{idx}"], "claim": f"no A{idx} are C{idx}", "expected_status": "accepted", "expected_channel": "negative_exclusion"})
        cases.append({"case_id": f"path_reverse_{idx:03d}", "premises": [f"all A{idx} are B{idx}"], "claim": f"all B{idx} are A{idx}", "expected_status": "rejected", "expected_channel": "reverse_inference_block"})
        cases.append({"case_id": f"path_identity_{idx:03d}", "premises": [f"all A{idx} are A{idx}"], "claim": f"all A{idx} are A{idx}", "expected_status": "rejected", "expected_channel": "identity_block"})
    return cases


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    write_jsonl(DATA, build_cases())
    report = evaluate_support_path_cases(load_jsonl(DATA))
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "release": "v10.7.0",
        "claim": "v10.7 creates typed support traces from bounded premise graphs instead of trusting supplied support labels.",
        "report_hash": canonical_hash(report),
        "all_gates_passed": report["all_gates_passed"],
        "metrics": {key: report[key] for key in report if key != "results"},
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
