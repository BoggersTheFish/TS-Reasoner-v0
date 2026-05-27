#!/usr/bin/env python3
"""Run a smoke pass over exported TensionLM-style candidate outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.tensionlm_adapter import load_tensionlm_export_jsonl, run_tensionlm_export_row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/real_tensionlm_candidate_adapter_cases.jsonl")
    parser.add_argument("--out", default="artifacts/real_tensionlm_candidate_adapter_smoke.json")
    args = parser.parse_args()

    rows = load_tensionlm_export_jsonl(ROOT / args.data)
    payloads = [run_tensionlm_export_row(row) for row in rows]
    smoke = {
        "adapter": "real_tensionlm_export_jsonl",
        "input": args.data,
        "case_count": len(payloads),
        "cases": payloads,
    }
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(smoke, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
