import unittest

from ts_reasoner.cig_checker import CIGChecker
from ts_reasoner.generator import DeterministicHeuristicGenerator
from ts_reasoner.ranker import HeuristicTensionRanker


class RankerTests(unittest.TestCase):
    def setUp(self):
        self.generator = DeterministicHeuristicGenerator()
        self.checker = CIGChecker()
        self.ranker = HeuristicTensionRanker()

    def test_valid_syllogism_lower_tension_than_invalid_jump(self):
        valid = self.generator.generate(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
        )[0]
        invalid = self.generator.generate(
            "If some A are B and all B are C, are all A C?",
            ["Some A are B.", "All B are C."],
        )[0]
        valid_score = self.ranker.score(valid, self.checker.check(valid))
        invalid_score = self.ranker.score(invalid, self.checker.check(invalid))
        self.assertLess(valid_score.global_tension, invalid_score.global_tension)
        self.assertIn("quantifier_jump", {issue.kind for issue in invalid_score.issues})

    def test_contradiction_detected(self):
        chain = self.generator.generate(
            "If all A are C and no A are C, are all A C?",
            ["All A are C.", "No A are C."],
        )[0]
        score = self.ranker.score(chain, self.checker.check(chain))
        self.assertIn("contradiction", {issue.kind for issue in score.issues})

    def test_missing_premise_detected(self):
        chain = self.generator.generate("Are all A C?", [])[0]
        score = self.ranker.score(chain, self.checker.check(chain))
        self.assertIn("missing_premise", {issue.kind for issue in score.issues})


if __name__ == "__main__":
    unittest.main()

