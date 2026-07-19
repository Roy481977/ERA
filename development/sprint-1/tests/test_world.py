"""Phase 1 tests: the world representation and navigation graph.

Run from the sprint-1 directory:  python3 -m unittest discover tests
"""

import unittest

from world.world import build_world
from world.navigation import NavigationGraph


class TestWorld(unittest.TestCase):
    def setUp(self):
        self.world = build_world()

    def test_five_locations(self):
        self.assertEqual(len(self.world.locations), 5)

    def test_world_is_valid(self):
        self.assertEqual(self.world.validate(), [])

    def test_graph_connected(self):
        self.assertTrue(self.world.nav.is_connected())

    def test_edges_symmetric(self):
        nav = self.world.nav
        for node in nav.nodes():
            for other, w in nav.neighbors(node):
                back = dict(nav.neighbors(other))
                self.assertIn(node, back)
                self.assertEqual(back[node], w)

    def test_no_islands(self):
        loc_ids = set(self.world.locations)
        self.assertEqual(set(self.world.nav.nodes()), loc_ids)

    def test_shortest_path_known(self):
        nav = self.world.nav
        # bakery -> riverside: via main square (1+2=3) beats via cafe (1+2=3);
        # both are 3, but the path must be deterministic and cost 3.
        self.assertEqual(nav.travel_time("loc_bakery", "loc_riverside"), 3)
        path = nav.shortest_path("loc_bakery", "loc_riverside")
        self.assertEqual(path[0], "loc_bakery")
        self.assertEqual(path[-1], "loc_riverside")

    def test_determinism(self):
        a = NavigationGraph().shortest_path("loc_stadium", "loc_riverside")
        b = NavigationGraph().shortest_path("loc_stadium", "loc_riverside")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
