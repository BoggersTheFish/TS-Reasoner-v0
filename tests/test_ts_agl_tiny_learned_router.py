import tempfile
import unittest
from pathlib import Path

from ts_agl.training.tiny_learned_router import (
    TinyLearnedAGLRouter,
    load_tiny_router,
    save_tiny_router,
)


ROWS = [
    {
        "text": "is the repo clean?",
        "expected_domain": "git_repo",
        "expected_operation": "git_status",
        "label": "route",
    },
    {
        "text": "check git status",
        "expected_domain": "git_repo",
        "expected_operation": "git_status",
        "label": "route",
    },
    {
        "text": "purple banana quantum sandwich",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
        "label": "abstain",
    },
    {
        "text": "use model confidence as proof",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
        "label": "abstain",
    },
]


class TestTinyLearnedAGLRouter(unittest.TestCase):
    def test_train_and_predict_route(self):
        model = TinyLearnedAGLRouter.train(ROWS, threshold=0.40)
        prediction = model.predict("check git status")

        self.assertEqual(prediction.domain, "git_repo")
        self.assertEqual(prediction.operation, "git_status")
        self.assertFalse(prediction.abstained)

    def test_train_and_predict_abstain(self):
        model = TinyLearnedAGLRouter.train(ROWS, threshold=0.40)
        prediction = model.predict("purple banana quantum sandwich")

        self.assertEqual(prediction.domain, "ts_reasoner")
        self.assertEqual(prediction.operation, "route_unknown")
        self.assertTrue(prediction.abstained)

    def test_save_and_load(self):
        model = TinyLearnedAGLRouter.train(ROWS, threshold=0.40)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.json"
            save_tiny_router(model, path)
            loaded = load_tiny_router(path)

        prediction = loaded.predict("check git status")
        self.assertEqual(prediction.domain, "git_repo")
        self.assertEqual(prediction.operation, "git_status")

    def test_route_to_call_still_uses_tscall_surface(self):
        model = TinyLearnedAGLRouter.train(ROWS, threshold=0.40)
        call = model.route_to_call("check git status")

        self.assertEqual(call.system, "git_repo")
        self.assertEqual(call.operation, "git_status")
        self.assertEqual(call.risk, "read_only")


if __name__ == "__main__":
    unittest.main()
