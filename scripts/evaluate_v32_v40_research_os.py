#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.research_os import write_v32_v40_receipts


def main() -> int:
    summary = write_v32_v40_receipts(
        ROOT / "artifacts",
        mission="prepare the next safe TS-Reasoner release candidate",
        repo=ROOT,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
