from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ts_reasoner.runtime_checkpoint_cli import checkpoint_session, restore_checkpoint_payload


ROOT = Path(__file__).resolve().parents[1]


class RuntimeCheckpointCliTests(unittest.TestCase):
    def test_checkpoint_session_creates_valid_checkpoint(self) -> None:
        session = json.loads((ROOT / 'data' / 'v9_7' / 'checkpoint_cli_good_session.json').read_text(encoding='utf-8'))

        exit_code, payload = checkpoint_session(session)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload['action'], 'checkpoint_created')
        self.assertEqual(payload['actions'], ['quarantine', 'open_repair'])
        self.assertTrue(payload['checkpoint_valid'])
        self.assertTrue(payload['restore_valid'])
        self.assertEqual(payload['candidate_graph_contamination_count'], 0)

    def test_restore_checkpoint_payload_restores_state(self) -> None:
        session = json.loads((ROOT / 'data' / 'v9_7' / 'checkpoint_cli_good_session.json').read_text(encoding='utf-8'))
        exit_code, payload = checkpoint_session(session)

        self.assertEqual(exit_code, 0)

        restore_code, restored = restore_checkpoint_payload(payload['checkpoint'])

        self.assertEqual(restore_code, 0)
        self.assertEqual(restored['action'], 'checkpoint_restored')
        self.assertEqual(restored['restored_state'], payload['checkpoint']['state'])
        self.assertEqual(restored['candidate_graph_contamination_count'], 0)

    def test_bad_session_rejected_safely(self) -> None:
        session = json.loads((ROOT / 'data' / 'v9_7' / 'checkpoint_cli_bad_session.json').read_text(encoding='utf-8'))

        exit_code, payload = checkpoint_session(session)

        self.assertEqual(exit_code, 2)
        self.assertEqual(payload['action'], 'invalid_input')
        self.assertEqual(payload['candidate_graph_contamination_count'], 0)

    def test_cli_checkpoint_and_restore_subprocess(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint_path = Path(tmp) / 'checkpoint.json'

            checkpoint_result = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'ts_reasoner.runtime_checkpoint_cli',
                    'checkpoint',
                    '--session',
                    '@data/v9_7/checkpoint_cli_good_session.json',
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(checkpoint_result.returncode, 0, msg=checkpoint_result.stdout + checkpoint_result.stderr)
            checkpoint_payload = json.loads(checkpoint_result.stdout)
            checkpoint_path.write_text(json.dumps(checkpoint_payload['checkpoint'], indent=2, sort_keys=True), encoding='utf-8')

            restore_result = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'ts_reasoner.runtime_checkpoint_cli',
                    'restore',
                    '--checkpoint',
                    '@' + str(checkpoint_path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(restore_result.returncode, 0, msg=restore_result.stdout + restore_result.stderr)
            restore_payload = json.loads(restore_result.stdout)
            self.assertEqual(restore_payload['action'], 'checkpoint_restored')
            self.assertEqual(restore_payload['candidate_graph_contamination_count'], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, 'scripts/v9_7/evaluate_runtime_checkpoint_cli.py'],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / 'artifacts' / 'runtime_checkpoint_cli_receipt.json').read_text(encoding='utf-8'))

        self.assertEqual(receipt['release'], 'v9.7.0')
        self.assertTrue(receipt['all_gates_passed'])
        self.assertEqual(receipt['candidate_graph_contamination_count'], 0)
        self.assertTrue(receipt['cli_creates_runtime_checkpoints'])
        self.assertTrue(receipt['cli_rejects_invalid_checkpoint_sessions'])
        self.assertTrue(receipt['checkpoint_restore_is_valid'])


if __name__ == '__main__':
    unittest.main()
