#!/usr/bin/env python3
"""Produce a deterministic live/export-style TensionLM candidate JSONL smoke."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/live_tensionlm_export_smoke_cases.jsonl")
    parser.add_argument("--out", default="artifacts/live_tensionlm_export_smoke.json")
    args = parser.parse_args()

    source_path = ROOT / args.cases
    out_path = ROOT / args.out
    rows = load_jsonl(source_path)
    export = {
        "export_mode": "simulated_external_tensionlm_export",
        "claim": "TensionLM-style outputs are exported as JSONL candidate data before verification.",
        "source_cases": str(source_path.relative_to(ROOT)),
        "row_count": len(rows),
        "rows": rows,
        "boundary": "Exported outputs remain candidate data and require TS-Reasoner typed verification.",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(export, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
