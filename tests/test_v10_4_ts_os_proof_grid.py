from __future__ import annotations

import unittest

from ts_reasoner.ts_os import ProofGridNode


class TSOSProofGridTests(unittest.TestCase):
    def test_export_pack_imports_supported_claims(self) -> None:
        source = ProofGridNode(state={"accepted_common_ground": ["power supports hospital"]})
        pack = source.export_pack()
        target = ProofGridNode()
        decision = target.import_pack(pack)

        self.assertEqual(decision.action, "imported")
        self.assertEqual(decision.accepted_claims, ("power supports hospital",))
        self.assertEqual(decision.receipt["candidate_graph_contamination_count"], 0)

    def test_bad_hash_is_rejected(self) -> None:
        pack = ProofGridNode(state={"accepted_common_ground": ["power supports hospital"]}).export_pack()
        pack["accepted_claims"].append("tampered")
        decision = ProofGridNode().import_pack(pack)
        self.assertEqual(decision.action, "rejected")

    def test_incompatible_channel_and_unsupported_claims_are_quarantined(self) -> None:
        incompatible = ProofGridNode(
            state={"accepted_common_ground": ["power supports hospital"]},
            manifest={"verifier_contract_ids": ["remote_only"], "channel_contracts": ["proof_boundary"]},
        ).export_pack()
        decision = ProofGridNode(manifest={"verifier_contract_ids": ["typed_verifier_support"]}).import_pack(incompatible)
        self.assertEqual(decision.action, "quarantined")
        self.assertEqual(decision.quarantined_claims, ("power supports hospital",))

        unsupported = ProofGridNode(state={"accepted_common_ground": ["unsupported: model confidence says water is restored"]}).export_pack()
        unsupported_decision = ProofGridNode().import_pack(unsupported)
        self.assertEqual(unsupported_decision.action, "quarantined")


if __name__ == "__main__":
    unittest.main()
