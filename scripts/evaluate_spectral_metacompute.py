#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_metacompute.spectral.evaluate import evaluate_spectral_cases
from ts_metacompute.spectral.receipts import build_spectral_receipt


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/spectral_cases.jsonl")
    parser.add_argument("--report", default="artifacts/spectral_metacompute_report.json")
    parser.add_argument("--receipt", default="artifacts/spectral_metacompute_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt
    report = evaluate_spectral_cases(load_jsonl(data_path))

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = build_spectral_receipt(root=ROOT, report=report, report_path=report_path, data_path=data_path)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["metrics"], indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] and receipt["receipt_schema_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
