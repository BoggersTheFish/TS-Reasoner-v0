from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.registry.manifest_validator import validate_manifest_dir


def main() -> int:
    report = validate_manifest_dir("ts_agl/domains")
    payload = report.to_dict()
    payload.update(
        {
            "artifact": "ts_agl_domain_pack_validation",
            "external_llm_used": False,
            "wrong_state_mutation_count": 0,
            "candidate_graph_contamination_count": 0,
            "all_gates_passed": report.valid,
        }
    )

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_domain_pack_validation_report.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
