#!/usr/bin/env python3
"""Train the v0.5 residual coupling matrix."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.coupling_learner import train_residual_coupling_matrix, write_coupling_artifact


ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    matrix, metadata = train_residual_coupling_matrix()
    model_path = write_coupling_artifact(
        ARTIFACTS / "learned_coupling_matrix_v05.json",
        matrix,
        metadata,
    )
    summary = {
        "model_path": str(model_path.relative_to(ROOT)),
        "coupling_matrix": matrix,
        "metadata": metadata,
        "claim": "v0.5 learns residual-calibrated tension coupling weights from v0.4 repair traces.",
    }
    (ARTIFACTS / "learned_coupling_matrix_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

