#!/usr/bin/env python3
"""Evaluate typed-channel calibrator ablations."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.calibration.calibrator import TypedChannelCalibrator
from ts_reasoner.calibration.train import evaluate_ablations


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def main() -> int:
    dataset_path = ROOT / "data" / "typed_channel_calibrator_dataset.jsonl"
    model_path = ROOT / "artifacts" / "typed_channel_calibrator.json"
    if not dataset_path.exists():
        raise SystemExit("missing dataset; run scripts/build_typed_calibrator_dataset.py first")
    if not model_path.exists():
        raise SystemExit("missing model; run scripts/train_typed_channel_calibrator.py first")
    rows = load_jsonl(dataset_path)
    calibrator = TypedChannelCalibrator.from_json(model_path)
    report = evaluate_ablations(rows, calibrator)
    report.update(
        {
            "headline": "Learned Typed-Channel Calibrator",
            "honest_claim": (
                "This release tests whether TS-Reasoner can learn to activate and prioritize "
                "typed tension channels from trace-level supervision, rather than learning "
                "reasoning behaviour end-to-end."
            ),
            "model_path": str(model_path.relative_to(ROOT)),
            "dataset": str(dataset_path.relative_to(ROOT)),
        }
    )
    report_path = ROOT / "artifacts" / "typed_channel_calibrator_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "project": "TS-Reasoner-v0",
        "version": "typed-channel-calibrator-v0",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": report["honest_claim"],
        "scope": "Trace-level typed-channel calibration over the existing small benchmark surface.",
        "inputs": [str(dataset_path.relative_to(ROOT)), str(model_path.relative_to(ROOT))],
        "commands_run": [
            "python3 scripts/build_typed_calibrator_dataset.py",
            "python3 scripts/train_typed_channel_calibrator.py",
            "python3 scripts/evaluate_typed_channel_calibrator.py",
        ],
        "tests": {},
        "benchmarks": report["ablations"],
        "artifacts": [
            {"path": str(model_path.relative_to(ROOT)), "sha256": sha256(model_path)},
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
        ],
        "known_limitations": [
            "Small curated dataset.",
            "Evaluates trace-level calibration, not broad reasoning generalization.",
            "Deterministic channel resolvers remain hand-coded operational priors.",
            "TensionLM is explicitly out of scope for this branch.",
        ],
        "tensions_detected": ["typed channels worked but had no learned calibration layer"],
        "tensions_resolved": ["added activation, weight, and resolver-priority calibrator ablations"],
        "unresolved_tensions": ["larger heldout channel traces and TensionLM candidate bridge remain future work"],
        "public_claim_level": "experimental",
    }
    receipt_path = ROOT / "artifacts" / "typed_channel_calibrator_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
