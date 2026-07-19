"""The World: the authoritative container for the district (DS-001 §1).

Assembles the five locations and the navigation graph and validates the
single-world-state invariants that matter in Phase 1:
  - every graph edge references a known location;
  - every location appears in the graph (no islands);
  - the graph is connected;
  - every location has at least one affordance.
"""

from __future__ import annotations

from dataclasses import dataclass

from .locations import LOCATIONS, Location
from .navigation import NavigationGraph


@dataclass(frozen=True)
class World:
    locations: dict[str, Location]
    nav: NavigationGraph

    def validate(self) -> list[str]:
        """Return a list of problems. Empty list == valid world."""
        problems: list[str] = []
        loc_ids = set(self.locations)
        graph_nodes = set(self.nav.nodes())

        for node in graph_nodes - loc_ids:
            problems.append(f"nav graph references unknown location: {node}")
        for loc in loc_ids - graph_nodes:
            problems.append(f"location not present in nav graph (island): {loc}")
        if not self.nav.is_connected():
            problems.append("navigation graph is not connected")
        for loc in self.locations.values():
            if not loc.affordances:
                problems.append(f"location has no affordances: {loc.id}")
        return problems


def build_world() -> World:
    """Construct the First Breath world. Deterministic."""
    return World(locations=dict(LOCATIONS), nav=NavigationGraph())
