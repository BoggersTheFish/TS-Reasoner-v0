#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_agl.os.verifier_first_local_agent_os import write_ts_os_v30


def main() -> int:
    report = write_ts_os_v30(ROOT / "artifacts" / "ts_os_v30_report.json", ROOT / "artifacts" / "ts_os_v30_receipt.json")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
