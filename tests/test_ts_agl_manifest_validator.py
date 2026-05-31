import unittest

from ts_agl.registry.manifest_validator import validate_manifest, validate_manifest_dir


class TestTSAGLManifestValidator(unittest.TestCase):
    def test_current_domain_pack_directory_is_valid(self):
        report = validate_manifest_dir("ts_agl/domains")
        self.assertTrue(report.valid, report.to_dict())
        self.assertGreaterEqual(report.manifest_count, 3)
        self.assertGreaterEqual(report.operation_count, 1)
        self.assertGreaterEqual(report.language_example_count, 1)

    def test_rejects_missing_domain(self):
        report = validate_manifest(
            {
                "description": "Broken pack",
                "node_types": [],
                "edge_types": [],
                "operations": [],
                "failure_modes": [],
            }
        )
        self.assertFalse(report.valid)
        self.assertGreater(report.error_count, 0)

    def test_rejects_risky_operation_without_confirmation(self):
        report = validate_manifest(
            {
                "domain": "bad_domain",
                "description": "Bad test domain",
                "node_types": ["thing"],
                "edge_types": ["relates_to"],
                "failure_modes": ["bad_state"],
                "operations": [
                    {
                        "name": "delete_thing",
                        "description": "Delete a thing.",
                        "required_inputs": ["thing_id"],
                        "risk": "destructive_write",
                        "requires_confirmation": False,
                        "examples": ["delete that thing"],
                    }
                ],
            }
        )
        self.assertFalse(report.valid)
        messages = " ".join(issue.message for issue in report.issues)
        self.assertIn("does not require confirmation", messages)

    def test_rejects_operation_without_examples(self):
        report = validate_manifest(
            {
                "domain": "bad_domain",
                "description": "Bad test domain",
                "node_types": ["thing"],
                "edge_types": ["relates_to"],
                "failure_modes": ["bad_state"],
                "operations": [
                    {
                        "name": "inspect_thing",
                        "description": "Inspect a thing.",
                        "required_inputs": [],
                        "risk": "read_only",
                        "requires_confirmation": False,
                        "examples": [],
                    }
                ],
            }
        )
        self.assertFalse(report.valid)
        messages = " ".join(issue.message for issue in report.issues)
        self.assertIn("requires at least one language example", messages)


if __name__ == "__main__":
    unittest.main()
