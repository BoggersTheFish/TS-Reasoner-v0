from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.arena.cross_domain_arena import (
    DEFAULT_CROSS_DOMAIN_REQUEST,
    run_cross_domain_arena,
    summarize_cross_domain_trace,
)


def evaluate() -> dict:
    trace = run_cross_domain_arena(DEFAULT_CROSS_DOMAIN_REQUEST)
    summary = summarize_cross_domain_trace(trace)

    expected_domains = {"git_repo", "filesystem", "ts_reasoner"}
    actual_domains = set(summary["domains"])
    expected_operations = {
        "git_repo.git_status",
        "git_repo.current_tag",
        "filesystem.list_files",
        "ts_reasoner.summarize_session",
        "git_repo.next_safe_release_action",
    }
    actual_operations = set(summary["operations"])

    report = {
        "artifact": "ts_agl_cross_domain_arena_report",
        "request": DEFAULT_CROSS_DOMAIN_REQUEST,
        "expected_domains": sorted(expected_domains),
        "actual_domains": sorted(actual_domains),
        "domain_coverage_rate": len(expected_domains & actual_domains) / len(expected_domains),
        "expected_operations": sorted(expected_operations),
        "actual_operations": sorted(actual_operations),
        "operation_coverage_rate": len(expected_operations & actual_operations) / len(expected_operations),
        "call_count": summary["call_count"],
        "all_calls_read_only": summary["all_calls_read_only"],
        "wrong_state_mutation_count": summary["wrong_state_mutation_count"],
        "candidate_graph_contamination_count": summary["candidate_graph_contamination_count"],
        "external_llm_used": summary["external_llm_used"],
        "statuses": summary["statuses"],
        "rendered_reply_present": bool(summary["rendered_reply"]),
        "all_gates_passed": (
            expected_domains <= actual_domains
            and expected_operations <= actual_operations
            and summary["all_calls_read_only"] is True
            and summary["wrong_state_mutation_count"] == 0
            and summary["candidate_graph_contamination_count"] == 0
            and summary["external_llm_used"] is False
            and bool(summary["rendered_reply"])
        ),
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_cross_domain_arena_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
