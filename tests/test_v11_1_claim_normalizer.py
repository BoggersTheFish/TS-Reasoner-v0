from __future__ import annotations

import unittest

from ts_reasoner.claim_normalizer import canonicalize_claim_surface, normalize_claim_surface
from ts_reasoner.support_path_verifier import verify_support_path


class ClaimNormalizerV111Tests(unittest.TestCase):
    def test_is_and_every_normalize_to_all_are(self) -> None:
        self.assertEqual(
            canonicalize_claim_surface("every generated output is candidate data"),
            "all generated output are candidate data",
        )
        self.assertEqual(
            canonicalize_claim_surface("all generated text is candidate data"),
            "all generated text are candidate data",
        )

    def test_negative_surfaces_normalize_to_no_are(self) -> None:
        self.assertEqual(
            canonicalize_claim_surface("no generated signal is proof"),
            "no generated signal are proof",
        )
        self.assertEqual(
            canonicalize_claim_surface("model confidence is not proof"),
            "no model confidence are proof",
        )

    def test_normalizer_reports_parse_metadata(self) -> None:
        observed = normalize_claim_surface("any model confidence signal is generated signal")
        self.assertEqual(observed["parse_status"], "parsed")
        self.assertEqual(observed["quantifier"], "all")
        self.assertEqual(observed["copula"], "is")

    def test_natural_transitive_chain_accepts(self) -> None:
        result = verify_support_path(
            [
                "every generated output is candidate data",
                "all candidate data are untrusted material",
            ],
            "all generated output is untrusted material",
        )
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["support"]["channel"], "transitive_all")

    def test_natural_negative_exclusion_accepts(self) -> None:
        result = verify_support_path(
            [
                "model confidence is generated signal",
                "no generated signal is proof",
            ],
            "model confidence is not proof",
        )
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["support"]["channel"], "negative_exclusion")

    def test_reverse_and_unsupported_remain_blocked(self) -> None:
        reverse = verify_support_path(
            ["generated text is candidate data"],
            "candidate data is generated text",
        )
        self.assertEqual(reverse["status"], "rejected")
        self.assertEqual(reverse["reason"], "reverse_inference_block")

        unsupported = verify_support_path(
            ["generated text is candidate data"],
            "generated text is proof",
        )
        self.assertEqual(unsupported["status"], "abstained")
        self.assertEqual(unsupported["reason"], "unsupported_claim")

    def test_identity_still_blocked(self) -> None:
        result = verify_support_path(["every fish is fish"], "all fish are fish")
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "identity_block")


if __name__ == "__main__":
    unittest.main()
