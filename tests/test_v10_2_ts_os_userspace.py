from __future__ import annotations

import sys
import unittest

from ts_reasoner.ts_os import run_userspace_app, schedule_next_budget


class TSOSUserspaceTests(unittest.TestCase):
    def test_malformed_json_abstains_and_shrinks_budget(self) -> None:
        result = run_userspace_app(
            f"{sys.executable} -c 'print(\"not json\")'",
            {"base_budget": 3, "initial_state": {}},
        )
        self.assertEqual(result.action, "userspace_abstained")
        self.assertLess(result.next_budget, 3)
        self.assertEqual(result.receipt["candidate_graph_contamination_count"], 0)

    def test_timeout_abstains(self) -> None:
        result = run_userspace_app(
            f"{sys.executable} -c 'import time; time.sleep(2)'",
            {"base_budget": 2, "initial_state": {}},
            timeout_seconds=0.05,
        )
        self.assertEqual(result.action, "userspace_abstained")

    def test_supported_and_unsupported_proposals_are_gated(self) -> None:
        code = (
            "import json; print(json.dumps({'schema':'ts_os_userspace_app_v1','candidates':["
            "{'requested_action':'accept_claim','payload':{'claim':'power supports water','support':['typed_verifier_support']}},"
            "{'requested_action':'accept_claim','payload':{'claim':'unsupported generated claim'}}]}))"
        )
        result = run_userspace_app(f"{sys.executable} -c {code!r}", {"base_budget": 3, "initial_state": {}})
        self.assertEqual(result.action, "userspace_completed")
        self.assertEqual([item.action for item in result.decisions], ["accepted", "repaired"])
        self.assertEqual(result.receipt["supported_candidates"], 1)

    def test_budget_scheduler_is_deterministic(self) -> None:
        self.assertEqual(
            schedule_next_budget(
                base_budget=3,
                supported_candidates=2,
                total_candidates=3,
                repair_targets_created=1,
                contamination=0,
                malformed=False,
            ),
            4,
        )


if __name__ == "__main__":
    unittest.main()
