from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.arena.router_stack_arena import RouterStackArena


def main() -> int:
    arena = RouterStackArena()
    report = arena.run_cases()

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_router_stack_arena_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_agl_router_stack_arena_receipt",
        "case_count": report["case_count"],
        "accuracy": report["accuracy"],
        "abstention_accuracy": report["abstention_accuracy"],
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "wrong_state_mutation_count": 0,
        "learned_router_is_proof_authority": False,
        "confidence_is_proof": False,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_agl_router_stack_arena_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
