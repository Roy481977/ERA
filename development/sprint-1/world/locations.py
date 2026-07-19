"""The five semantic locations of the first district (DS-001 §1).

A Location is a *logical* place with semantic affordances — not a graphical
asset. Affordances (not coordinates) are what intentions/schedules resolve
against, per world-state-schema.md.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """A semantic place. Immutable identity; affordances are semantic tags."""

    id: str
    name: str
    affordances: tuple[str, ...]


# The five locations of the First Breath district. Ordered for stable output.
LOCATIONS: dict[str, Location] = {
    "loc_stadium": Location(
        "loc_stadium", "Stadium",
        ("WORK_GROUNDSKEEP", "MATCH_GATE", "GATHER"),
    ),
    "loc_main_square": Location(
        "loc_main_square", "Main Square",
        ("MARKET", "KIOSK", "SIT_BENCH", "BUSK", "GATHER"),
    ),
    "loc_bakery": Location(
        "loc_bakery", "Bakery",
        ("WORK_BAKERY_COUNTER", "BUY_BREAD", "HOME"),
    ),
    "loc_cafe": Location(
        "loc_cafe", "Café",
        ("WORK", "DRINK_COFFEE", "LEGENDS_CORNER", "HOME"),
    ),
    "loc_riverside": Location(
        "loc_riverside", "Riverside",
        ("WALK", "SIT_BENCH", "VISIT_OAK", "HOME"),
    ),
}


def all_location_ids() -> tuple[str, ...]:
    return tuple(LOCATIONS.keys())
