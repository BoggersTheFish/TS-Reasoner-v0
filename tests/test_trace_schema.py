import json
import tempfile
import unittest
from pathlib import Path

from ts_reasoner import run_reasoner
from ts_reasoner.trace import write_json


TOP_LEVEL_KEYS = {
    "question",
    "premises",
    "candidates",
    "selected_chain",
    "tension_score",
    "cig_check",
    "repairs",
    "final_answer",
    "trace",
}

TRACE_KEYS = {
    "contract_version",
    "pipeline",
    "input",
    "generator",
    "ranker",
    "tension_coordinator",
    "operation_router",
    "selection",
    "candidate_scores",
    "chosen_action",
    "rejected_alternatives",
    "settled_answer",
    "failure_reason",
    "coordinated_tension_field",
    "operation_loop",
    "candidate_operation_loops",
    "graph_view",
}


class TraceSchemaTests(unittest.TestCase):
    def test_v1_public_trace_contract_keys_are_stable(self):
        output = run_reasoner(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
        )
        data = output.to_dict()

        self.assertEqual(set(data), TOP_LEVEL_KEYS)
        self.assertTrue(TRACE_KEYS.issubset(set(data["trace"])))
        self.assertIsInstance(data["candidates"], list)
        self.assertIsInstance(data["repairs"], list)
        self.assertIsInstance(data["trace"]["candidate_scores"], list)
        self.assertIsInstance(data["trace"]["candidate_operation_loops"], dict)
        self.assertEqual(data["trace"]["contract_version"], "1.0.0")
        self.assertEqual(data["trace"]["input"]["question"], data["question"])
        self.assertEqual(data["trace"]["input"]["premises"], data["premises"])
        self.assertEqual(data["trace"]["settled_answer"], data["final_answer"])
        self.assertIsInstance(data["trace"]["rejected_alternatives"], list)
        self.assertIn("selected_op", data["trace"]["chosen_action"])
        self.assertIn("local_tension", data["trace"]["candidate_scores"][0])

    def test_serialized_trace_contract_is_json_compatible(self):
        output = run_reasoner(
            "If all seeds are plants and all plants are living and all living are need_water, are all seeds need_water?",
            ["All seeds are plants.", "All plants are living.", "All living are need_water."],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(output, Path(tmp) / "trace.json")
            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(set(data), TOP_LEVEL_KEYS)
        self.assertEqual(data["trace"]["pipeline"], "TS-Reasoner-v0")
        self.assertEqual(data["final_answer"], "all seeds are need_water.")

    def test_failure_reason_is_recorded_for_unsettled_candidates(self):
        output = run_reasoner(
            "If all A are B because all A are B, are all A B?",
            ["All A are B because all A are B."],
        )
        loop = output.trace["candidate_operation_loops"]["candidate_direct"]

        self.assertFalse(loop["settled"])
        self.assertIn("status", loop)
        self.assertEqual(output.trace["failure_reason"], output.trace["operation_loop"]["status"])


if __name__ == "__main__":
    unittest.main()
