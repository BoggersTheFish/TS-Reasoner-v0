import tempfile
import unittest
from pathlib import Path

from scripts.run_ts_agl_domain_pack_generator import build_demo_spec
from ts_agl.registry import DomainRegistry
from ts_agl.registry.manifest_validator import validate_manifest
from ts_agl.router.example_router import TeachingExampleRouter
from ts_agl.teaching import (
    DomainTeachingSpec,
    OperationTeachingSpec,
    generate_domain_pack,
    write_generated_domain_pack,
)


class TestTSAGLDomainPackGenerator(unittest.TestCase):
    def test_generates_valid_demo_pack(self):
        manifest = generate_domain_pack(build_demo_spec())
        report = validate_manifest(manifest)

        self.assertTrue(report.valid, report.to_dict())
        self.assertEqual(manifest["domain"], "research_notes")
        self.assertGreaterEqual(len(manifest["operations"]), 3)

    def test_risky_generated_operations_require_confirmation(self):
        manifest = generate_domain_pack(build_demo_spec())
        risky_ops = [op for op in manifest["operations"] if op["risk"] != "read_only"]

        self.assertTrue(risky_ops)
        self.assertTrue(all(op["requires_confirmation"] for op in risky_ops))

    def test_generated_pack_routes_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "research_notes.json"
            manifest = write_generated_domain_pack(build_demo_spec(), path)

            registry = DomainRegistry(tmp).load()
            router = TeachingExampleRouter(registry)

            for operation in manifest["operations"]:
                for example in operation["examples"]:
                    call = router.call_from_example(example)
                    self.assertEqual(call.system, manifest["domain"])
                    self.assertEqual(call.operation, operation["name"])

    def test_invalid_risk_is_rejected(self):
        spec = DomainTeachingSpec(
            domain="bad_domain",
            description="Bad domain",
            node_types=["thing"],
            edge_types=["relates_to"],
            failure_modes=["bad_state"],
            operations=[
                OperationTeachingSpec(
                    name="bad_op",
                    description="Bad operation",
                    required_inputs=[],
                    risk="not_a_real_risk",
                    examples=["do bad thing"],
                )
            ],
        )

        with self.assertRaises(ValueError):
            generate_domain_pack(spec)


if __name__ == "__main__":
    unittest.main()
