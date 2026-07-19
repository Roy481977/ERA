"""The navigation graph of the first district (DS-001 §1).

Undirected weighted graph; edge weight = travel time in WorldClock ticks.
Movement happens along edges over travel time — no teleporting (AT-5).
Deterministic: neighbours and paths are returned in stable, sorted order.
"""

from __future__ import annotations

import heapq

# (a, b, travel_time_in_ticks). Undirected. Main Square is the hub.
EDGES: tuple[tuple[str, str, int], ...] = (
    ("loc_main_square", "loc_bakery", 1),
    ("loc_main_square", "loc_cafe", 1),
    ("loc_main_square", "loc_stadium", 2),
    ("loc_main_square", "loc_riverside", 2),
    ("loc_bakery", "loc_cafe", 1),
    ("loc_cafe", "loc_riverside", 2),
)


class NavigationGraph:
    """Undirected weighted graph over location ids."""

    def __init__(self, edges: tuple[tuple[str, str, int], ...] = EDGES) -> None:
        self._adj: dict[str, dict[str, int]] = {}
        for a, b, w in edges:
            if w <= 0:
                raise ValueError(f"edge {a}-{b} must have positive travel time")
            self._adj.setdefault(a, {})[b] = w
            self._adj.setdefault(b, {})[a] = w

    def nodes(self) -> tuple[str, ...]:
        return tuple(sorted(self._adj))

    def neighbors(self, node: str) -> tuple[tuple[str, int], ...]:
        """Neighbours as (location_id, travel_time), sorted for determinism."""
        return tuple(sorted(self._adj.get(node, {}).items()))

    def travel_time(self, a: str, b: str) -> int:
        """Shortest travel time between a and b (Dijkstra)."""
        return self._dijkstra(a)[0][b]

    def shortest_path(self, a: str, b: str) -> list[str]:
        """Node path from a to b inclusive (deterministic)."""
        dist, prev = self._dijkstra(a)
        if b not in dist:
            raise KeyError(b)
        path = [b]
        while path[-1] != a:
            path.append(prev[path[-1]])
        return list(reversed(path))

    def is_connected(self) -> bool:
        """True if every node is reachable from every other node."""
        nodes = self.nodes()
        if not nodes:
            return True
        reachable = set(self._dijkstra(nodes[0])[0])
        return set(nodes).issubset(reachable)

    def _dijkstra(self, source: str) -> tuple[dict[str, int], dict[str, str]]:
        dist: dict[str, int] = {source: 0}
        prev: dict[str, str] = {}
        pq: list[tuple[int, str]] = [(0, source)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, float("inf")):
                continue
            for v, w in sorted(self._adj.get(u, {}).items()):
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        return dist, prev
