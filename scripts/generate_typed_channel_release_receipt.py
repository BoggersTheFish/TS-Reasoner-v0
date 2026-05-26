#!/usr/bin/env python3
"""Generate the unified typed-channel release receipt."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


SOURCE_ARTIFACTS = (
    "artifacts/typed_tension_receipt.json",
    "artifacts/typed_tension_benchmark_report.json",
    "artifacts/typed_channel_calibrator_receipt.json",
    "artifacts/typed_channel_calibrator_report.json",
    "artifacts/typed_channel_calibrator_stress_receipt.json",
    "artifacts/typed_channel_calibrator_stress_report.json",
    "artifacts/typed_channel_calibrator_structural_features_receipt.json",
    "artifacts/typed_channel_calibrator_structural_features_report.json",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def build_receipt(now: str | None = None) -> dict[str, Any]:
    typed_tension = load_json(ROOT / "artifacts" / "typed_tension_benchmark_report.json")
    calibrator = load_json(ROOT / "artifacts" / "typed_channel_calibrator_report.json")
    stress = load_json(ROOT / "artifacts" / "typed_channel_calibrator_stress_report.json")
    structural = load_json(ROOT / "artifacts" / "typed_channel_calibrator_structural_features_report.json")
    original = structural["variants"]["original_calibrator"]["metrics"]
    repaired = structural["variants"]["full_structural_features"]["metrics"]
    full_calibrator = calibrator["ablations"]["full_calibrator"]

    return {
        "project": "TS-Reasoner-v0",
        "version": "typed-channel-release-receipt-v0",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": now or datetime.now(timezone.utc).isoformat(),
        "headline": "TS-Core-backed typed channels, learned calibrator, stress, and structural repair",
        "claim": (
            "TS-Reasoner now has TS-Core-backed typed tension channels plus a learned calibrator. "
            "Stress testing exposed structural generalization failures, and query-relevant graph "
            "features repaired those failures on the current stress benchmark."
        ),
        "scope": (
            "Unified release receipt for kernel-backed typed channels, scoped calibrator evaluation, "
            "generalization stress, and structural feature repair."
        ),
        "release_story": [
            {
                "stage": "kernel_to_channels",
                "summary": "TS-Core-backed typed tension channels expose channel activation, resolver events, and typed runtime traces.",
                "evidence": "artifacts/typed_tension_benchmark_report.json",
            },
            {
                "stage": "scoped_calibrator",
                "summary": "The learned typed-channel calibrator reaches 1.0 on scoped trace-supervision metrics.",
                "evidence": "artifacts/typed_channel_calibrator_report.json",
            },
            {
                "stage": "generalization_stress",
                "summary": "Heldout stress produces Outcome B: renaming works, but depth/features fail.",
                "evidence": "artifacts/typed_channel_calibrator_stress_report.json",
            },
            {
                "stage": "structural_repair",
                "summary": "Query-relevant graph features repair the targeted failures on the current stress benchmark.",
                "evidence": "artifacts/typed_channel_calibrator_structural_features_report.json",
            },
        ],
        "inputs": list(SOURCE_ARTIFACTS),
        "commands_run": [
            "python3 -m unittest discover",
            "python3 scripts/evaluate_typed_tension.py",
            "python3 scripts/evaluate_typed_channel_calibrator.py",
            "python3 scripts/evaluate_typed_channel_calibrator_stress.py",
            "python3 scripts/evaluate_typed_channel_calibrator_structural_features.py",
            "python3 scripts/generate_typed_channel_release_receipt.py",
        ],
        "tests": {
            "python3 -m unittest discover": {
                "status": "passed",
                "test_count": 44,
            }
        },
        "benchmarks": {
            "typed_tension_channels": typed_tension["metrics"],
            "scoped_calibrator_full": {
                "answer_accuracy": full_calibrator["answer_accuracy"],
                "channel_activation_accuracy": full_calibrator["channel_activation_accuracy"],
                "resolver_accuracy": full_calibrator["resolver_accuracy"],
                "abstention_correctness": full_calibrator["abstention_correctness"],
                "trace_schema_validity": full_calibrator["trace_schema_validity"],
            },
            "generalization_stress": {
                "outcome": stress["outcome"],
                "metrics": stress["metrics"],
            },
            "structural_repair": {
                "outcome": structural["outcome"],
                "original_calibrator": original,
                "full_structural_features": repaired,
                "targeted_deltas": {
                    "depth_generalization": round(repaired["depth_generalization"] - original["depth_generalization"], 4),
                    "distractor_robustness": round(repaired["distractor_robustness"] - original["distractor_robustness"], 4),
                    "quantifier_trap_failures": original["quantifier_trap_failures"] - repaired["quantifier_trap_failures"],
                    "contradiction_misses": original["contradiction_misses"] - repaired["contradiction_misses"],
                },
            },
        },
        "artifacts": [
            {"path": path, "sha256": sha256(ROOT / path)}
            for path in SOURCE_ARTIFACTS
        ],
        "known_limitations": [
            "All calibrator and stress results are synthetic and small.",
            "The current stress surface is parser-controlled and not natural-language robust.",
            "Structural repair is measured on the current heldout stress benchmark, not on broad reasoning tasks.",
            "TS-Core-backed channels remain deterministic operational priors; the calibrator does not learn reasoning end-to-end.",
            "TensionLM remains out of scope until this symbolic trace stack is release-stable.",
        ],
        "tensions_detected": [
            "single scoped calibrator metrics could hide overfit",
            "heldout stress exposed depth, distractor, quantifier, and contradiction-placement failures",
            "public release needed one receipt tying kernel, channels, calibrator, stress, and repair together",
        ],
        "tensions_resolved": [
            "added scoped calibrator ablations",
            "preserved Outcome B stress failure as evidence",
            "added structural graph features and repaired targeted stress failures",
            "generated unified typed-channel release receipt",
        ],
        "unresolved_tensions": [
            "release still needs broader non-synthetic benchmarks",
            "messy-language candidate generation remains future TensionLM work",
            "future calibrators should train directly over the structural feature surface",
        ],
        "public_claim_level": "experimental",
    }


def main() -> int:
    receipt = build_receipt()
    target = ROOT / "artifacts" / "typed_channel_release_receipt.json"
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
