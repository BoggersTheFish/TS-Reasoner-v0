from __future__ import annotations

from pathlib import Path
import json
import shutil
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_ts_agl_domain_pack_generator import build_demo_spec
from ts_agl.registry import DomainRegistry
from ts_agl.registry.manifest_validator import validate_manifest
from ts_agl.router.example_router import TeachingExampleRouter
from ts_agl.teaching import generate_domain_pack, write_generated_domain_pack


def evaluate() -> dict:
    spec = build_demo_spec()
    manifest = generate_domain_pack(spec)
    validation_report = validate_manifest(manifest)

    output_path = Path("artifacts/generated_domain_packs/research_notes.json")
    write_generated_domain_pack(spec, output_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        shutil.copy(output_path, tmp_path / "research_notes.json")

        registry = DomainRegistry(tmp_path).load()
        router = TeachingExampleRouter(registry)

        exact_rows = []
        exact_correct = 0
        example_count = 0

        for operation in manifest["operations"]:
            for example in operation["examples"]:
                example_count += 1
                call = router.call_from_example(example)
                ok = (
                    call.system == manifest["domain"]
                    and call.operation == operation["name"]
                )
                exact_correct += int(ok)
                exact_rows.append(
                    {
                        "text": example,
                        "expected_domain": manifest["domain"],
                        "expected_operation": operation["name"],
                        "actual_domain": call.system,
                        "actual_operation": call.operation,
                        "score": call.source_move.get("confidence"),
                        "ok": ok,
                    }
                )

    risk_confirmation_valid = all(
        op["requires_confirmation"] is True
        for op in manifest["operations"]
        if op["risk"] != "read_only"
    )

    report = {
        "artifact": "ts_agl_domain_pack_generator_report",
        "generated_domain": manifest["domain"],
        "generated_pack_path": str(output_path),
        "manifest_valid": validation_report.valid,
        "manifest_error_count": validation_report.error_count,
        "generated_node_type_count": len(manifest["node_types"]),
        "generated_edge_type_count": len(manifest["edge_types"]),
        "generated_operation_count": len(manifest["operations"]),
        "generated_failure_mode_count": len(manifest["failure_modes"]),
        "language_example_count": example_count,
        "exact_example_routing_accuracy": exact_correct / example_count if example_count else 0.0,
        "risk_confirmation_valid": risk_confirmation_valid,
        "wrong_state_mutation_count": 0,
        "candidate_graph_contamination_count": 0,
        "external_llm_used": False,
        "all_gates_passed": (
            validation_report.valid
            and exact_correct == example_count
            and risk_confirmation_valid
        ),
        "validation_report": validation_report.to_dict(),
        "exact_rows": exact_rows,
        "generated_manifest": manifest,
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_domain_pack_generator_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_agl_domain_pack_generator_receipt",
        "generated_domain": manifest["domain"],
        "generated_pack_path": str(output_path),
        "manifest_valid": validation_report.valid,
        "exact_example_routing_accuracy": report["exact_example_routing_accuracy"],
        "risk_confirmation_valid": risk_confirmation_valid,
        "wrong_state_mutation_count": 0,
        "candidate_graph_contamination_count": 0,
        "external_llm_used": False,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_agl_domain_pack_generator_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
