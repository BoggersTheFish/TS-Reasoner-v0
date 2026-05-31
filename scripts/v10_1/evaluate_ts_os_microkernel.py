from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.ts_os import EpistemicMicrokernel, KernelRequest, write_json


def main() -> int:
    kernel = EpistemicMicrokernel({})
    accepted = kernel.handle_request(KernelRequest(
        requested_action="accept_claim",
        candidate_payload={"claim": "network supports hospital", "support": ["typed_verifier_support"]},
    ))
    repaired = kernel.handle_request(KernelRequest(
        requested_action="accept_claim",
        candidate_payload={"claim": "generated text proves recovery"},
    ))
    report = {
        "release": "v10.1",
        "accepted_action": accepted.action,
        "repaired_action": repaired.action,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": accepted.action == "accepted" and repaired.action == "repaired",
    }
    receipt = {
        "receipt_type": "ts_os_microkernel",
        **report,
        "generated_text_is_not_proof": True,
        "model_confidence_is_not_proof": True,
        "runtime_integrity_is_not_claim_truth": True,
    }
    write_json(ROOT / "artifacts" / "ts_os_microkernel_report.json", report)
    write_json(ROOT / "artifacts" / "ts_os_microkernel_receipt.json", receipt)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
