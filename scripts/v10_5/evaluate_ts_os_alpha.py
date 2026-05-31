from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_os import run_alpha_scenario, write_json


def main() -> int:
    scenario = json.loads((ROOT / "data" / "v10_5" / "ts_os_alpha_scenario.json").read_text(encoding="utf-8"))
    payload = run_alpha_scenario(scenario)
    write_json(ROOT / "artifacts" / "ts_os_alpha_report.json", payload)
    write_json(ROOT / "artifacts" / "ts_os_alpha_receipt.json", payload["receipt"])
    print(json.dumps(payload["receipt"], indent=2, sort_keys=True))
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
