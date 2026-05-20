import unittest

from ts_reasoner import ReasonerOutput, run_reasoner
from ts_reasoner.generator import LearnedCandidateGenerator, train_learned_candidate_generator
from ts_reasoner.synthetic_data import candidate_dataset_rows, train_eval_split


class LearnedCandidateGeneratorTests(unittest.TestCase):
    def test_trained_generator_proposes_reasoning_chains(self):
        train_rows, _eval_rows = train_eval_split(candidate_dataset_rows())
        generator = train_learned_candidate_generator(train_rows)
        chains = generator.generate(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
        )
        self.assertTrue(chains)
        self.assertTrue(all(chain.steps for chain in chains))
        self.assertIn("candidate_cautious", {chain.chain_id for chain in chains})

    def test_pipeline_schema_preserved_with_learned_generator(self):
        train_rows, _eval_rows = train_eval_split(candidate_dataset_rows())
        generator = train_learned_candidate_generator(train_rows)
        output = run_reasoner(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
            generator=generator,
        )
        self.assertIsInstance(output, ReasonerOutput)
        self.assertEqual(output.trace["generator"], "LearnedCandidateGenerator")
        self.assertIn("candidate_scores", output.trace)

    def test_generator_can_roundtrip_json(self):
        generator = LearnedCandidateGenerator({"candidate_cautious": 1.0})
        self.assertEqual("LearnedCandidateGenerator", generator.name)
        chains = generator.generate("Are all A C?", [])
        self.assertTrue(chains)


if __name__ == "__main__":
    unittest.main()

