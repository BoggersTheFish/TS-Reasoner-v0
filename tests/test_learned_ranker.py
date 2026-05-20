import unittest

from ts_reasoner import ReasonerOutput, run_reasoner
from ts_reasoner.generator import DeterministicHeuristicGenerator
from ts_reasoner.learned_ranker import LearnedTensionRanker, train_logistic_ranker
from ts_reasoner.ranker import HeuristicTensionRanker
from ts_reasoner.synthetic_data import candidate_dataset_rows, train_eval_split
from ts_reasoner.types import TensionScore


class LearnedRankerTests(unittest.TestCase):
    def test_learned_ranker_returns_tension_score_schema(self):
        rows = candidate_dataset_rows()
        train_rows, _eval_rows = train_eval_split(rows)
        learned = train_logistic_ranker(train_rows, epochs=80, learning_rate=0.08)
        chain = DeterministicHeuristicGenerator().generate(
            "If some A are B and all B are C, are all A C?",
            ["Some A are B.", "All B are C."],
        )[0]
        score = learned.score(chain)
        self.assertIsInstance(score, TensionScore)
        self.assertEqual(score.chain_id, chain.chain_id)
        self.assertIn("s1", score.local_tension)
        self.assertGreaterEqual(score.global_tension, 0.0)
        self.assertLessEqual(score.global_tension, 1.0)

    def test_pipeline_output_schema_matches_with_learned_ranker(self):
        rows = candidate_dataset_rows()
        train_rows, _eval_rows = train_eval_split(rows)
        learned = train_logistic_ranker(train_rows, epochs=80, learning_rate=0.08)
        question = "If all A are B and all B are C, are all A C?"
        premises = ["All A are B.", "All B are C."]
        heuristic_output = run_reasoner(question, premises, ranker=HeuristicTensionRanker())
        learned_output = run_reasoner(question, premises, ranker=learned)
        self.assertIsInstance(learned_output, ReasonerOutput)
        self.assertEqual(set(heuristic_output.to_dict().keys()), set(learned_output.to_dict().keys()))
        self.assertEqual(set(heuristic_output.trace.keys()), set(learned_output.trace.keys()))


if __name__ == "__main__":
    unittest.main()

