#!/usr/bin/env python3
"""Write a compact TensionLM candidate bridge demo artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.candidate_bridge import run_tensionlm_candidate_bridge


def main() -> None:
    payload = run_tensionlm_candidate_bridge(
        "All A are B. All B are C. Are all A C?",
        mode="mock",
    )
    target = ROOT / "artifacts" / "tensionlm_candidate_bridge_demo.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
