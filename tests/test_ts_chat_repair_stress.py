import json
import tempfile
import unittest
from pathlib import Path

from ts_chat.repair_stress import (
    build_stress_base_session,
    contradiction_claim_for_cycle,
    run_long_run_self_repair_stress,
    stress_report_valid,
)


class TestTSChatRepairStress(unittest.TestCase):
    def test_build_stress_base_session(self):
        session = build_stress_base_session()

        self.assertEqual(len(session.accepted_claim_texts()), 5)
        self.assertEqual(len(session.repair_targets), 1)
        self.assertFalse(session.external_llm_used)

    def test_contradiction_claim_for_cycle_deterministic(self):
        self.assertEqual(contradiction_claim_for_cycle(1), "no cats are mortal")
        self.assertEqual(contradiction_claim_for_cycle(2), "no dogs are mortal")
        self.assertEqual(contradiction_claim_for_cycle(3), "no birds are mortal")
        self.assertEqual(contradiction_claim_for_cycle(4), "no fish are mortal")
        self.assertEqual(contradiction_claim_for_cycle(5), "no cats are mortal")

    def test_long_run_stress_report_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_long_run_self_repair_stress(cycles=8, work_dir=Path(tmp))

            self.assertEqual(report["schema"], "ts_chat_long_run_self_repair_stress_v1")
            self.assertEqual(report["release"], "v6.9.0")
            self.assertEqual(report["cycles"], 8)
            self.assertEqual(report["passed_cycles"], 8)
            self.assertEqual(report["failed_cycles"], 0)
            self.assertEqual(report["cycle_pass_rate"], 1.0)
            self.assertEqual(report["wrong_accept_count"], 0)
            self.assertTrue(report["accepted_claims_preserved"])
            self.assertTrue(report["unsupported_claims_not_promoted"])
            self.assertEqual(report["candidate_graph_contamination_count"], 0)
            self.assertEqual(report["session_reload_failures"], 0)
            self.assertEqual(report["knowledge_pack_roundtrip_failures"], 0)
            self.assertEqual(report["revision_candidate_failures"], 0)
            self.assertEqual(report["provenance_failures"], 0)
            self.assertTrue(report["all_gates_passed"])
            self.assertTrue(stress_report_valid(report))

    def test_long_run_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            report = run_long_run_self_repair_stress(cycles=3, work_dir=work_dir)

            self.assertTrue((work_dir / "latest_stress_session.json").exists())
            self.assertTrue((work_dir / "cycle_001_knowledge_pack.json").exists())
            self.assertTrue((work_dir / "cycle_001_imported_session.json").exists())
            self.assertTrue(stress_report_valid(report))

    def test_stress_report_invalid_if_wrong_accept(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_long_run_self_repair_stress(cycles=3, work_dir=Path(tmp))
            report["wrong_accept_count"] = 1

            self.assertFalse(stress_report_valid(report))

    def test_stress_dataset_exists(self):
        path = Path("data/ts_chat_long_run_stress_v69.jsonl")
        self.assertTrue(path.exists())

        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["claim"], "no cats are mortal")


if __name__ == "__main__":
    unittest.main()
