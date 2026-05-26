#!/usr/bin/env python3
"""Train the tiny typed-channel calibrator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.calibration.train import train_calibrator


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    dataset_path = ROOT / "data" / "typed_channel_calibrator_dataset.jsonl"
    if not dataset_path.exists():
        raise SystemExit("missing dataset; run scripts/build_typed_calibrator_dataset.py first")
    rows = load_jsonl(dataset_path)
    calibrator = train_calibrator(rows)
    model_path = calibrator.to_json(ROOT / "artifacts" / "typed_channel_calibrator.json")
    summary = {
        "model_path": str(model_path.relative_to(ROOT)),
        "dataset": str(dataset_path.relative_to(ROOT)),
        "training_rows": len(rows),
        "channels": calibrator.metadata.get("channels", []),
        "claim": "Learned Typed-Channel Calibrator trains channel activation, weights, and resolver priority from trace supervision.",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
