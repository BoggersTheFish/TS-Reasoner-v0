#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_agl.os.evidence_dashboard import build_ts_evidence_dashboard


def main() -> int:
    dashboard = build_ts_evidence_dashboard(ROOT)
    target = ROOT / "artifacts" / "ts_evidence_dashboard.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(dashboard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(dashboard, indent=2, sort_keys=True))
    return 0 if dashboard["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
