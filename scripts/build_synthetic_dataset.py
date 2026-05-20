#!/usr/bin/env python3
"""Build synthetic candidate-chain dataset for v1 learned ranker."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.synthetic_data import candidate_dataset_rows


DATA = ROOT / "data"


def main() -> int:
    DATA.mkdir(exist_ok=True)
    rows = candidate_dataset_rows()
    path = DATA / "synthetic_ranker_dataset.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    summary = {
        "rows": len(rows),
        "positive_labels": sum(int(row["label"]) for row in rows),
        "negative_labels": sum(1 - int(row["label"]) for row in rows),
        "path": str(path.relative_to(ROOT)),
    }
    (DATA / "synthetic_ranker_dataset_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
