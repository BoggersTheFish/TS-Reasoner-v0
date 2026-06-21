import unittest

from ts_reasoner.topology import (
    Connection, ConnectionEvidence, ConnectionStatus, SpatialTopology, connection_id,
)


class HabitatV3TopologyTests(unittest.TestCase):
    def edge(self, a, b, status=ConnectionStatus.OPEN, direction="bidirectional", evidence="e1"):
        identity = connection_id(a, b, direction)
        return Connection(identity, a, b, direction, status, source_ids=(evidence,), evidence=(ConnectionEvidence(evidence, status, (evidence,)),))

    def test_no_implicit_edge_and_indirect_route(self):
        topology = SpatialTopology()
        topology.merge(self.edge("hall", "kitchen", evidence="hk"))
        topology.merge(self.edge("kitchen", "garden", evidence="kg"))
        self.assertEqual(topology.traversable("hall", "garden")[2], "NO_CONNECTION")
        path, support, _ = topology.route("hall", "garden")
        self.assertEqual(path, ("hall", "kitchen", "garden"))
        self.assertIn("hk", support)

    def test_direction_is_enforced(self):
        topology = SpatialTopology()
        topology.merge(self.edge("hall", "courtyard", direction="directed"))
        self.assertTrue(topology.traversable("hall", "courtyard")[0])
        self.assertFalse(topology.traversable("courtyard", "hall")[0])

    def test_conflicting_evidence_is_not_traversable(self):
        topology = SpatialTopology()
        topology.merge(self.edge("hall", "kitchen", ConnectionStatus.OPEN, evidence="open"))
        topology.merge(self.edge("hall", "kitchen", ConnectionStatus.BLOCKED, evidence="blocked"))
        edge = next(iter(topology.connections.values()))
        self.assertEqual(edge.status, ConnectionStatus.CONFLICTED)
        self.assertFalse(topology.traversable("hall", "kitchen")[0])

    def test_duplicate_identity_merges_provenance(self):
        topology = SpatialTopology()
        topology.merge(self.edge("hall", "kitchen", evidence="one"))
        topology.merge(self.edge("kitchen", "hall", evidence="two"))
        self.assertEqual(len(topology.connections), 1)
        self.assertEqual(len(next(iter(topology.connections.values())).evidence), 2)

    def test_cycle_safe_and_bounded(self):
        topology = SpatialTopology()
        topology.merge(self.edge("a", "b", evidence="ab"))
        topology.merge(self.edge("b", "c", evidence="bc"))
        topology.merge(self.edge("c", "a", evidence="ca"))
        self.assertEqual(topology.route("a", "missing", max_states=2)[0], ())


if __name__ == "__main__":
    unittest.main()
