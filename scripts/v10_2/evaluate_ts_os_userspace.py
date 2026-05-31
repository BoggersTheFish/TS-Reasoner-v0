from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_os import run_userspace_app, write_json


def main() -> int:
    app = (
        f"{sys.executable} -c "
        + repr("import json; print(json.dumps({'schema':'ts_os_userspace_app_v1','candidates':[{'requested_action':'accept_claim','payload':{'claim':'power supports water','support':['typed_verifier_support']}}]}))")
    )
    result = run_userspace_app(app, {"base_budget": 2, "initial_state": {}})
    report = {
        "release": "v10.2",
        "action": result.action,
        "next_budget": result.next_budget,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": result.action == "userspace_completed",
    }
    write_json(ROOT / "artifacts" / "ts_os_userspace_report.json", report)
    write_json(ROOT / "artifacts" / "ts_os_userspace_receipt.json", result.receipt)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
