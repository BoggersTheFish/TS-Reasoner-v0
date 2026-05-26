#!/usr/bin/env python3
"""Write a compact typed tension demo artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner import run_reasoner


CASES = [
    {
        "name": "valid_transitivity",
        "question": "If all A are B and all B are C, are all A C?",
        "premises": ["All A are B.", "All B are C."],
    },
    {
        "name": "reverse_fallacy",
        "question": "If all A are B and all B are C, are all C A?",
        "premises": ["All A are B.", "All B are C."],
    },
    {
        "name": "some_all_unsupported",
        "question": "If some pilots are engineers and all engineers are careful, are all pilots careful?",
        "premises": ["Some pilots are engineers.", "All engineers are careful."],
    },
]


def main() -> None:
    artifact = []
    for case in CASES:
        output = run_reasoner(case["question"], case["premises"])
        artifact.append(
            {
                "name": case["name"],
                "question": case["question"],
                "premises": case["premises"],
                "answer": output.final_answer,
                "tension_channels": output.trace["tension_channels"],
                "typed_runtime": output.trace["typed_runtime"],
            }
        )
    target = ROOT / "artifacts" / "typed_tension_demo.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
