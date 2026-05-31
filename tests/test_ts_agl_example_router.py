import unittest

from ts_agl.registry import DomainRegistry
from ts_agl.router.example_router import TeachingExampleRouter


class TestTSAGLExampleRouter(unittest.TestCase):
    def setUp(self):
        self.registry = DomainRegistry().load()
        self.router = TeachingExampleRouter(self.registry)

    def test_routes_filesystem_phrase_from_domain_examples(self):
        call = self.router.call_from_example("what folder is this?")
        self.assertEqual(call.system, "filesystem")
        self.assertEqual(call.operation, "pwd")

    def test_routes_list_files_phrase_from_domain_examples(self):
        call = self.router.call_from_example("show this folder")
        self.assertEqual(call.system, "filesystem")
        self.assertEqual(call.operation, "list_files")

    def test_routes_git_status_phrase_from_domain_examples(self):
        call = self.router.call_from_example("is the repo clean?")
        self.assertEqual(call.system, "git_repo")
        self.assertEqual(call.operation, "git_status")

    def test_unknown_low_confidence_abstains_to_route_unknown(self):
        call = self.router.call_from_example("purple banana quantum sandwich")
        self.assertEqual(call.system, "ts_reasoner")
        self.assertEqual(call.operation, "route_unknown")

    def test_explain_route_has_ranked_candidates(self):
        explanation = self.router.explain_route("what tag is at HEAD?")
        self.assertIn("selected", explanation)
        self.assertIn("ranked", explanation)
        self.assertGreaterEqual(len(explanation["ranked"]), 1)


if __name__ == "__main__":
    unittest.main()
