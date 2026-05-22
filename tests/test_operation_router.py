import unittest

from ts_reasoner.cig_checker import CIGChecker
from ts_reasoner.generator import DeterministicHeuristicGenerator
from ts_reasoner.operation_router import OperationRouter
from ts_reasoner.ranker import HeuristicTensionRanker
from ts_reasoner.tension_agents import TensionCoordinator
from ts_reasoner.types import ReasoningChain, ReasoningStep


class OperationRouterTests(unittest.TestCase):
    def setUp(self):
        self.generator = DeterministicHeuristicGenerator()
        self.checker = CIGChecker()
        self.ranker = HeuristicTensionRanker()
        self.coordinator = TensionCoordinator()
        self.router = OperationRouter(
            checker=self.checker,
            ranker=self.ranker,
            coordinator=self.coordinator,
        )

    def test_quantifier_jump_is_repaired_and_rescored(self):
        chain = self.generator.generate(
            "If some A are B and all B are C, are all A C?",
            ["Some A are B.", "All B are C."],
        )[0]
        cig = self.checker.check(chain)
        score = self.ranker.score(chain, cig)
        field = self.coordinator.coordinate(chain, cig, score)
        transition = self.router.run_once(chain, cig, score, field)

        self.assertEqual(transition["status"], "repaired")
        self.assertEqual(transition["selected_op"], "REPAIR_STEP")
        self.assertLess(transition["score"].global_tension, score.global_tension)
        self.assertLess(transition["after"]["coordinated_tensions"]["logic"], field["coordinated_tensions"]["logic"])
        self.assertIn("some", transition["chain"].steps[-1].text.lower())

    def test_valid_chain_is_accepted_without_mutation(self):
        chain = self.generator.generate(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
        )[0]
        cig = self.checker.check(chain)
        score = self.ranker.score(chain, cig)
        field = self.coordinator.coordinate(chain, cig, score)
        transition = self.router.run_once(chain, cig, score, field)

        self.assertEqual(transition["status"], "accepted")
        self.assertIs(transition["chain"], chain)
        self.assertEqual(transition["residual"]["logic"], 0.0)

    def test_run_until_stable_can_use_repair_then_compression(self):
        chain = ReasoningChain(
            chain_id="multi_error",
            question="If some A are B and all B are C, are all A C?",
            premises=["Some A are B.", "All B are C."],
            steps=[
                ReasoningStep("p1", "Some A are B.", "premise", [], 0.9),
                ReasoningStep("p2", "All B are C.", "premise", [], 0.9),
                ReasoningStep("s1", "Therefore all A are C.", "conclusion", ["p1", "p2"], 0.95),
                ReasoningStep("s2", "Therefore some A are C.", "conclusion", ["p1", "p2"], 0.7),
            ],
            final_answer="all A are C.",
        )

        loop = self.router.run_until_stable(chain, max_steps=5)

        self.assertTrue(loop["settled"])
        self.assertGreaterEqual(loop["cycle_count"], 2)
        self.assertEqual(loop["cycles"][0]["status"], "repaired")
        self.assertIn("compressed", {cycle["status"] for cycle in loop["cycles"]})
        self.assertEqual(loop["final"]["global_tension"], 0.0)

    def test_redundant_nonpremise_claim_compression_closes_contradiction_case(self):
        chain = ReasoningChain(
            chain_id="contradiction_forced_answer",
            question="If all A are C and no A are C, are all A C?",
            premises=["All A are C.", "No A are C."],
            steps=[
                ReasoningStep("p1", "All A are C.", "premise", [], 0.9),
                ReasoningStep("p2", "No A are C.", "premise", [], 0.9),
                ReasoningStep("s1", "Certainly all A are C.", "conclusion", ["p1", "p2"], 0.98),
            ],
            final_answer="Certainly all A are C.",
        )

        loop = self.router.run_until_stable(chain, max_steps=5)

        self.assertTrue(loop["settled"])
        self.assertEqual(loop["status"], "settled")
        self.assertEqual([cycle["status"] for cycle in loop["cycles"]], ["repaired", "repaired", "compressed"])


if __name__ == "__main__":
    unittest.main()
