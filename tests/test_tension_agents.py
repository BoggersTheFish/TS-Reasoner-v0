import unittest

from ts_reasoner.cig_checker import CIGChecker
from ts_reasoner.generator import DeterministicHeuristicGenerator
from ts_reasoner.ranker import HeuristicTensionRanker
from ts_reasoner.tension_agents import TensionCoordinator


class TensionAgentTests(unittest.TestCase):
    def setUp(self):
        self.generator = DeterministicHeuristicGenerator()
        self.checker = CIGChecker()
        self.ranker = HeuristicTensionRanker()
        self.coordinator = TensionCoordinator()

    def test_invalid_transition_wakes_repair_and_goal_channels(self):
        chain = self.generator.generate(
            "If some A are B and all B are C, are all A C?",
            ["Some A are B.", "All B are C."],
        )[0]
        cig = self.checker.check(chain)
        score = self.ranker.score(chain, cig)
        field = self.coordinator.coordinate(chain, cig, score)

        self.assertGreater(field["raw_tensions"]["logic"], 0.0)
        self.assertGreater(field["coordinated_tensions"]["repair"], field["raw_tensions"]["repair"])
        self.assertGreater(field["coordinated_tensions"]["goal"], field["raw_tensions"]["goal"])
        self.assertIn(field["selected_next_op"], {"REPAIR_STEP", "CHECK_ENTAILMENT", "LOCALIZE_FAILURE"})
        self.assertEqual(field["target"], "s1")

    def test_stable_trace_accepts_without_repair_pressure(self):
        chain = self.generator.generate(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
        )[0]
        cig = self.checker.check(chain)
        score = self.ranker.score(chain, cig)
        field = self.coordinator.coordinate(chain, cig, score)

        self.assertEqual(field["selected_next_op"], "ACCEPT_TRACE")
        self.assertEqual(field["coordinated_tensions"]["logic"], 0.0)
        self.assertIsNone(field["target"])


if __name__ == "__main__":
    unittest.main()
