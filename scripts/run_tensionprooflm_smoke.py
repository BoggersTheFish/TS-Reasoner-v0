#!/usr/bin/env python3
"""Run the tiny TensionProofLM target smoke-training/eval receipt."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.tensionproof_smoke import evaluate_tensionproof_smoke  # noqa: E402


ARTIFACTS = ROOT / "artifacts"
REPORT = ARTIFACTS / "tensionprooflm_smoke_report.json"


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    report = evaluate_tensionproof_smoke()
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
