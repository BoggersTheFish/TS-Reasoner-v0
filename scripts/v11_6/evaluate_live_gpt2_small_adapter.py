from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.gpt2_boundary.live_gpt2_adapter import LiveGPT2Config, evaluate_live_gpt2_adapter

CONFIG = ROOT / "data" / "v11_6" / "live_gpt2_adapter_config.json"
REPORT = ROOT / "artifacts" / "v11_6" / "live_gpt2_adapter_report.json"
RECEIPT = ROOT / "artifacts" / "v11_6" / "live_gpt2_adapter_receipt.json"


def main() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    payload["run_live"] = bool(payload.get("run_live", False) or os.environ.get("TS_REASONER_RUN_LIVE_GPT2") == "1")
    config = LiveGPT2Config(**payload)

    report = evaluate_live_gpt2_adapter(config)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "receipt_type": "v11_6_live_gpt2_adapter_receipt",
        "release": "v11.6.0",
        "claim": "TS-Reasoner provides an optional live GPT-2-small adapter for verifier-first boundary comparison.",
        "model_name": report["model_name"],
        "task_count": report["task_count"],
        "adapter_contract_passed": report["adapter_contract_passed"],
        "live_gpt2_requested": report["dependency_status"]["live_requested"],
        "live_gpt2_available": report["live_gpt2_available"],
        "live_gpt2_generation_completed_rate": report["live_gpt2_generation_completed_rate"],
        "live_gpt2_answer_accuracy": report["live_gpt2_answer_accuracy"],
        "ts_reasoner_wrong_accept_count": report["ts_reasoner_wrong_accept_count"],
        "ts_reasoner_accepted_without_typed_support_count": report["ts_reasoner_accepted_without_typed_support_count"],
        "ts_reasoner_candidate_graph_contamination_count": report["ts_reasoner_candidate_graph_contamination_count"],
        "all_gates_passed": report["all_gates_passed"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not report["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
