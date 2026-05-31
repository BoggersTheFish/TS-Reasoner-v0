from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_replay_cli import replay_session


ROOT = Path(__file__).resolve().parents[1]


class RuntimeReplayCliTests(unittest.TestCase):
    def test_replay_session_routes_multi_event_session(self) -> None:
        session = json.loads((ROOT / 'data' / 'v9_3' / 'runtime_replay_cli_session.json').read_text(encoding='utf-8'))

        exit_code, payload = replay_session(session)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload['action'], 'replay_completed')
        self.assertEqual(payload['actions'], ['quarantine', 'open_repair', 'branch_world'])
        self.assertEqual(payload['candidate_graph_contamination_count'], 0)

    def test_bad_session_rejected_safely(self) -> None:
        session = json.loads((ROOT / 'data' / 'v9_3' / 'runtime_replay_cli_bad_session.json').read_text(encoding='utf-8'))

        exit_code, payload = replay_session(session)

        self.assertEqual(exit_code, 2)
        self.assertEqual(payload['action'], 'invalid_input')
        self.assertEqual(payload['candidate_graph_contamination_count'], 0)

    def test_cli_subprocess_outputs_replay_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                '-m',
                'ts_reasoner.runtime_replay_cli',
                'replay',
                '--session',
                '@data/v9_3/runtime_replay_cli_session.json',
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload['action'], 'replay_completed')
        self.assertEqual(payload['actions'], ['quarantine', 'open_repair', 'branch_world'])
        self.assertEqual(payload['candidate_graph_contamination_count'], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, 'scripts/v9_3/evaluate_runtime_replay_cli.py'],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / 'artifacts' / 'runtime_replay_cli_receipt.json').read_text(encoding='utf-8'))

        self.assertEqual(receipt['release'], 'v9.3.0')
        self.assertTrue(receipt['all_gates_passed'])
        self.assertEqual(receipt['candidate_graph_contamination_count'], 0)
        self.assertTrue(receipt['cli_replays_multi_event_sessions'])
        self.assertTrue(receipt['invalid_replay_sessions_rejected_safely'])


if __name__ == '__main__':
    unittest.main()
