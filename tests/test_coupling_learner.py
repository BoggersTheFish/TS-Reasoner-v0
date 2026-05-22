import tempfile
import unittest
from pathlib import Path

from ts_reasoner import run_reasoner
from ts_reasoner.coupling_learner import train_residual_coupling_matrix, write_coupling_artifact
from ts_reasoner.tension_agents import TensionCoordinator


class CouplingLearnerTests(unittest.TestCase):
    def test_trains_nonempty_residual_coupling_matrix(self):
        matrix, metadata = train_residual_coupling_matrix()

        self.assertGreater(metadata["repair_examples"], 0)
        self.assertIn("logic", matrix)
        self.assertIn("repair", matrix["logic"])
        self.assertGreater(matrix["logic"]["repair"], 0.0)

    def test_learned_matrix_round_trips_into_reasoner(self):
        matrix, metadata = train_residual_coupling_matrix()
        with tempfile.TemporaryDirectory() as tmp:
            path = write_coupling_artifact(Path(tmp) / "couplings.json", matrix, metadata)
            coordinator = TensionCoordinator.from_json(path)
            output = run_reasoner(
                "If some A are B and all B are C, are all A C?",
                ["Some A are B.", "All B are C."],
                tension_coordinator=coordinator,
            )

        direct_loop = output.trace["candidate_operation_loops"]["candidate_direct"]
        self.assertEqual(direct_loop["status"], "settled")
        self.assertEqual(direct_loop["cycles"][0]["status"], "repaired")
        self.assertEqual(direct_loop["final"]["global_tension"], 0.0)


if __name__ == "__main__":
    unittest.main()
