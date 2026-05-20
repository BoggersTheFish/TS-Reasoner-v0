import unittest

from ts_reasoner.cig_checker import CIGChecker
from ts_reasoner.generator import DeterministicHeuristicGenerator
from ts_reasoner.ranker import HeuristicTensionRanker
from ts_reasoner.repair import TensionRepairer


class RepairTests(unittest.TestCase):
    def test_quantifier_jump_produces_traceable_repair(self):
        chain = DeterministicHeuristicGenerator().generate(
            "If some A are B and all B are C, are all A C?",
            ["Some A are B.", "All B are C."],
        )[0]
        checker = CIGChecker()
        score = HeuristicTensionRanker().score(chain, checker.check(chain))
        repairs = TensionRepairer().suggest(chain, score)
        quantifier_repairs = [repair for repair in repairs if repair.issue_kind == "quantifier_jump"]
        self.assertTrue(quantifier_repairs)
        self.assertEqual(quantifier_repairs[0].target_step_id, "s1")
        self.assertIn("some", quantifier_repairs[0].proposed_text.lower())


if __name__ == "__main__":
    unittest.main()

