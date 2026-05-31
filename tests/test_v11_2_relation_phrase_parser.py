from __future__ import annotations

import unittest

from ts_reasoner.claim_normalizer import canonicalize_claim_surface
from ts_reasoner.relation_phrase_parser import parse_relation_phrase
from ts_reasoner.support_path_verifier import verify_support_path


class RelationPhraseParserV112Tests(unittest.TestCase):
    def test_positive_relation_phrases_normalize(self) -> None:
        cases = {
            "fish belongs to animals": "all fish are animals",
            "salmon is a kind of fish": "all salmon are fish",
            "candidate data is a type of untrusted material": "all candidate data are untrusted material",
            "generated text counts as candidate data": "all generated text are candidate data",
            "typed support implies proof authority": "all typed support are proof authority",
            "accepted proof requires typed support": "all accepted proof are typed support",
        }
        for surface, expected in cases.items():
            with self.subTest(surface=surface):
                self.assertEqual(canonicalize_claim_surface(surface), expected)

    def test_negative_relation_phrases_normalize(self) -> None:
        cases = {
            "model confidence cannot be proof": "no model confidence are proof",
            "generated text can not be proof": "no generated text are proof",
            "candidate data excludes proof": "no candidate data are proof",
        }
        for surface, expected in cases.items():
            with self.subTest(surface=surface):
                self.assertEqual(canonicalize_claim_surface(surface), expected)

    def test_parse_metadata(self) -> None:
        parsed = parse_relation_phrase("generated text counts as candidate data")
        self.assertEqual(parsed["parse_status"], "parsed")
        self.assertEqual(parsed["quantifier"], "all")
        self.assertEqual(parsed["relation"], "counts_as")

    def test_relation_transitive_accepts(self) -> None:
        result = verify_support_path(
            [
                "generated text counts as candidate data",
                "candidate data is a type of untrusted material",
            ],
            "generated text is untrusted material",
        )
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["support"]["channel"], "transitive_all")

    def test_negative_relation_direct_support_accepts(self) -> None:
        result = verify_support_path(
            ["model confidence cannot be proof"],
            "model confidence is not proof",
        )
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["support"]["channel"], "direct_support")

    def test_reverse_and_unsupported_still_blocked(self) -> None:
        reverse = verify_support_path(
            ["generated text counts as candidate data"],
            "candidate data counts as generated text",
        )
        self.assertEqual(reverse["status"], "rejected")
        self.assertEqual(reverse["reason"], "reverse_inference_block")

        unsupported = verify_support_path(
            ["generated text counts as candidate data"],
            "generated text counts as proof",
        )
        self.assertEqual(unsupported["status"], "abstained")
        self.assertEqual(unsupported["reason"], "unsupported_claim")


if __name__ == "__main__":
    unittest.main()
