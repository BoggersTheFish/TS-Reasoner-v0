#!/usr/bin/env python3
"""Run a small TS-Reasoner v3 demo from generated artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.train_v3_verifier_guided_model import (
    predict_channels,
    predict_quality,
    predict_status,
)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    model_path = ROOT / "artifacts/v3/verifier_guided_candidate_model.json"
    data_path = ROOT / "artifacts/v3/v3_training_dataset.jsonl"
    report_path = ROOT / "artifacts/v3/verifier_guided_candidate_model_report.json"

    model = json.loads(model_path.read_text(encoding="utf-8"))
    rows = load_jsonl(data_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))

    demo_row = next(row for row in rows if row["split"] == "stress")
    status_weights = model["weights"]["status_head"]
    channel_weights = model["weights"]["channel_heads"]
    quality_weights = model["weights"]["quality_head"]

    predicted_status = predict_status(status_weights, demo_row)
    predicted_channels = predict_channels(channel_weights, demo_row)
    predicted_quality = predict_quality(quality_weights, predicted_status)

    payload = {
        "demo": "TS-Reasoner v3.0 verifier-guided candidate model",
        "input_claim": demo_row["input_claim"],
        "candidate_id": demo_row["candidate_id"],
        "target_status": demo_row["target"]["status"],
        "predicted_status": predicted_status,
        "target_channels": demo_row["target"]["channels"],
        "predicted_channels": predicted_channels,
        "predicted_quality": predicted_quality,
        "proof_boundary": {
            "model_role": "prediction only",
            "verifier_role": "typed verifier remains proof authority",
            "proof_role": "model prediction is not proof",
        },
        "gate_summary": report["gates"],
    }

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
