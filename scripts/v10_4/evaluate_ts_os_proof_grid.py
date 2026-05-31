from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_os import ProofGridNode, write_json


def main() -> int:
    source = ProofGridNode(state={"accepted_common_ground": ["power supports hospital"]})
    pack = source.export_pack()
    decision = ProofGridNode().import_pack(pack)
    report = {
        "release": "v10.4",
        "import_action": decision.action,
        "accepted_claims": list(decision.accepted_claims),
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": decision.action == "imported",
    }
    write_json(ROOT / "artifacts" / "proof_grid_pack.json", pack)
    write_json(ROOT / "artifacts" / "ts_os_proof_grid_report.json", report)
    write_json(ROOT / "artifacts" / "ts_os_proof_grid_receipt.json", decision.receipt)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
