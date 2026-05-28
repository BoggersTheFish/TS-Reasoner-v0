#!/usr/bin/env python3
"""Generate v2.8 verifier trace training-loop smoke receipt."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report_path = ROOT / "artifacts/verifier_trace_training_loop_smoke_report.json"
    model_path = ROOT / "artifacts/verifier_trace_status_model_v28.json"
    source_path = ROOT / "data/verifier_trace_training_data_v27.jsonl"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    receipt = {
        "project": "TS-Reasoner-v0",
        "version": "v2.8.0-training-loop-smoke",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "v2.7 verifier trace rows can train a tiny supervised status model above simple baselines.",
        "scope": "Smoke-scale linear classifier over exported verifier trace rows; not a broad model-training claim.",
        "commands_run": [
            "python3 scripts/train_from_verifier_trace_smoke.py",
            "python3 scripts/generate_verifier_trace_training_loop_smoke_receipt.py",
            "python3 -m unittest discover -q",
        ],
        "metrics": report["metrics"],
        "row_count": report["row_count"],
        "train_rows": report["train_rows"],
        "eval_rows": report["eval_rows"],
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
            {"path": str(model_path.relative_to(ROOT)), "sha256": sha256(model_path)},
            {"path": str(source_path.relative_to(ROOT)), "sha256": sha256(source_path)},
        ],
        "boundary": report["boundary"],
        "known_limitations": [
            "Smoke-scale linear model only.",
            "Uses synthetic/benchmark-derived verifier traces.",
            "No TensionLM runtime is loaded.",
            "No neural language model is trained.",
            "Trained model is not proof authority.",
        ],
        "public_claim_level": "experimental",
    }

    out = ROOT / "artifacts/verifier_trace_training_loop_smoke_receipt.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
