#!/usr/bin/env python3
"""Build trace-level rows for the typed-channel calibrator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.calibration.train import build_rows


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    cases = load_jsonl(ROOT / "data" / "typed_tension_benchmark.jsonl")
    rows = build_rows(cases)
    target = ROOT / "data" / "typed_channel_calibrator_dataset.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    summary = {
        "dataset": str(target.relative_to(ROOT)),
        "source": "data/typed_tension_benchmark.jsonl",
        "case_count": len(cases),
        "row_count": len(rows),
        "rows_per_case": len(rows) // max(1, len(cases)),
        "claim": "Rows supervise typed-channel activation/resolution, not end-to-end reasoning behavior.",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
