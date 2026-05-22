import json
import tempfile
import unittest
from pathlib import Path

from ts_reasoner import ReasonerOutput, run_reasoner
from ts_reasoner.trace import write_json


class PipelineTests(unittest.TestCase):
    def test_pipeline_returns_complete_output_and_trace_shape(self):
        output = run_reasoner(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
        )
        self.assertIsInstance(output, ReasonerOutput)
        self.assertEqual(output.selected_chain.chain_id, "candidate_cautious")
        self.assertIn("candidate_scores", output.trace)
        self.assertIn("graph_view", output.trace)
        self.assertIn("coordinated_tension_field", output.trace)
        self.assertIn("agents", output.trace["coordinated_tension_field"])
        self.assertIn("operation_loop", output.trace)
        self.assertIn("candidate_operation_loops", output.trace)
        self.assertEqual(output.final_answer, "all A are C.")

    def test_write_json_trace(self):
        output = run_reasoner("If all A are B and all B are C, are all A C?")
        with tempfile.TemporaryDirectory() as tmp:
            path = write_json(output, Path(tmp) / "trace.json")
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["trace"]["pipeline"], "TS-Reasoner-v0")
            self.assertIn("selected_chain", data)
            self.assertIn("tension_score", data)
            self.assertIn("coordinated_tension_field", data["trace"])
            self.assertIn("operation_loop", data["trace"])


if __name__ == "__main__":
    unittest.main()
