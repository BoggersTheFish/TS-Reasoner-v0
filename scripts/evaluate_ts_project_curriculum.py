#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_agl.os.ts_project_curriculum import write_ts_project_curriculum


def main() -> int:
    report = write_ts_project_curriculum(
        ROOT / "artifacts" / "ts_project_curriculum_report.json",
        ROOT / "artifacts" / "ts_project_curriculum_receipt.json",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
