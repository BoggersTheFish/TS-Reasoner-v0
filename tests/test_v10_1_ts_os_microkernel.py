from __future__ import annotations

import unittest

from ts_reasoner.ts_os import EpistemicMicrokernel, KernelRequest, canonical_hash


class TSOSMicrokernelTests(unittest.TestCase):
    def test_kernel_state_is_immutable_and_read_only(self) -> None:
        kernel = EpistemicMicrokernel({"accepted_common_ground": ["Power Supports Hospital"]})
        with self.assertRaises(AttributeError):
            kernel.state.accepted_common_ground = ("mutated",)  # type: ignore[misc]
        with self.assertRaises(TypeError):
            kernel.read_only_state()["accepted_common_ground"] = ("mutated",)  # type: ignore[index]

    def test_unsupported_claim_opens_repair_without_accepting(self) -> None:
        kernel = EpistemicMicrokernel({})
        decision = kernel.handle_request(KernelRequest(
            requested_action="accept_claim",
            candidate_payload={"claim": "generated text proves hospital status"},
            userspace_app_id="test",
        ))

        self.assertEqual(decision.action, "repaired")
        self.assertEqual(decision.state.accepted_common_ground, ())
        self.assertEqual(len(decision.state.repair_targets), 1)
        self.assertEqual(decision.receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(decision.receipt["generated_text_is_not_proof"])

    def test_supported_claim_mutates_only_through_gate_and_hashes_receipt(self) -> None:
        kernel = EpistemicMicrokernel({})
        decision = kernel.handle_request(KernelRequest(
            requested_action="accept_claim",
            candidate_payload={"claim": "Network reroute supports hospital", "support": ["typed_verifier_support"]},
            userspace_app_id="test",
        ))

        self.assertEqual(decision.action, "accepted")
        self.assertEqual(decision.state.accepted_common_ground, ("network reroute supports hospital",))
        receipt = dict(decision.receipt)
        observed_hash = receipt.pop("receipt_hash")
        receipt["receipt_hash"] = ""
        self.assertEqual(observed_hash, canonical_hash(receipt))


if __name__ == "__main__":
    unittest.main()
