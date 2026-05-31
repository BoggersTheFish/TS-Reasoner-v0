import unittest

from ts_agl.registry import DomainRegistry


class TestTSAGLRegistry(unittest.TestCase):
    def test_loads_domains(self):
        registry = DomainRegistry().load()
        domains = registry.list_domains()
        self.assertIn("git_repo", domains)
        self.assertIn("ts_reasoner", domains)
        self.assertIn("filesystem", domains)

    def test_finds_operation(self):
        registry = DomainRegistry().load()
        op = registry.find_operation("git_repo", "git_status")
        self.assertIsNotNone(op)
        self.assertEqual(op["risk"], "read_only")


if __name__ == "__main__":
    unittest.main()
