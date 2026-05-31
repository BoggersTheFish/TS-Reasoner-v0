from __future__ import annotations

import unittest

from ts_reasoner.paragraph_decomposer import decompose_paragraph, question_to_claim
from ts_reasoner.support_path_verifier import verify_support_path


class ParagraphDecomposerV113Tests(unittest.TestCase):
    def test_question_to_claim(self) -> None:
        self.assertEqual(question_to_claim("Are fish organisms?"), "all fish are organisms")
        self.assertEqual(question_to_claim("Is model confidence not proof?"), "no model confidence are proof")
        self.assertEqual(question_to_claim("Can generated text be proof?"), "all generated text are proof")

    def test_transitive_paragraph_accepts(self) -> None:
        observed = decompose_paragraph("All fish are animals. All animals are organisms. Are fish organisms?")
        self.assertEqual(observed["status"], "parsed")
        self.assertEqual(observed["premises"], ["all fish are animals", "all animals are organisms"])
        self.assertEqual(observed["candidate_claim"], "all fish are organisms")

        result = verify_support_path(observed["premises"], observed["candidate_claim"])
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["support"]["channel"], "transitive_all")

    def test_relation_paragraph_accepts(self) -> None:
        observed = decompose_paragraph(
            "Generated text counts as candidate data. Candidate data is a type of untrusted material. Is generated text untrusted material?"
        )
        self.assertEqual(observed["candidate_claim"], "all generated text are untrusted material")
        result = verify_support_path(observed["premises"], observed["candidate_claim"])
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["support"]["channel"], "transitive_all")

    def test_reverse_and_unsupported_remain_blocked(self) -> None:
        reverse = decompose_paragraph("Generated text counts as candidate data. Is candidate data generated text?")
        reverse_result = verify_support_path(reverse["premises"], reverse["candidate_claim"])
        self.assertEqual(reverse_result["status"], "rejected")
        self.assertEqual(reverse_result["reason"], "reverse_inference_block")

        unsupported = decompose_paragraph("Generated text counts as candidate data. Can generated text be proof?")
        unsupported_result = verify_support_path(unsupported["premises"], unsupported["candidate_claim"])
        self.assertEqual(unsupported_result["status"], "abstained")
        self.assertEqual(unsupported_result["reason"], "unsupported_claim")

    def test_ambiguous_input_safely_abstains(self) -> None:
        observed = decompose_paragraph("Blah maybe fish possibly. Why though?")
        self.assertEqual(observed["status"], "abstained")
        self.assertEqual(observed["candidate_claim"], "")


if __name__ == "__main__":
    unittest.main()
