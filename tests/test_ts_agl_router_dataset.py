import tempfile
import unittest
from pathlib import Path
import json

from ts_agl.registry import DomainRegistry
from ts_agl.training import build_router_dataset, write_router_dataset_jsonl
from ts_agl.training.router_dataset import collect_trace_rows


class TestTSAGLRouterDataset(unittest.TestCase):
    def test_build_dataset_has_routes_and_abstentions(self):
        rows = build_router_dataset(DomainRegistry().load())
        labels = {row.label for row in rows}

        self.assertIn("route", labels)
        self.assertIn("abstain", labels)
        self.assertGreater(len(rows), 0)

    def test_dataset_contains_risk_rows(self):
        rows = build_router_dataset(DomainRegistry().load())
        risks = {row.risk for row in rows}

        self.assertIn("read_only", risks)
        self.assertIn("reversible_write", risks)
        self.assertIn("external_side_effect", risks)

    def test_write_dataset_jsonl(self):
        rows = build_router_dataset(DomainRegistry().load())

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dataset.jsonl"
            write_router_dataset_jsonl(rows, path)

            self.assertTrue(path.exists())
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), len(rows))
            first = json.loads(lines[0])
            self.assertIn("text", first)
            self.assertIn("expected_domain", first)
            self.assertIn("expected_operation", first)

    def test_collect_trace_rows_from_nested_trace(self):
        payload = {
            "trace": {
                "raw_text": "do several things",
                "calls": [
                    {
                        "system": "git_repo",
                        "operation": "git_status",
                        "risk": "read_only",
                        "requires_confirmation": False,
                    }
                ],
            }
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows = collect_trace_rows([path])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].expected_domain, "git_repo")
        self.assertEqual(rows[0].expected_operation, "git_status")
        self.assertTrue(rows[0].source.startswith("trace:"))


if __name__ == "__main__":
    unittest.main()
