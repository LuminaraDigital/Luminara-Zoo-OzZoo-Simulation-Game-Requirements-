"""Optional starter content aligned with the Luminara Zoo tutorial narrative."""

from __future__ import annotations

from typing import List

from zoo.zoo import Zoo

# Opening balance described in student Tutorial documentation (AUD).
LUMINARA_STARTER_FUNDS = 75_000.0

_STARTER_ADOPTIONS: List[tuple[str, str]] = [
    ("koala", "Kiki"),
    ("koala", "Karl"),
    ("kangaroo", "Joey"),
    ("kangaroo", "Sheila"),
    ("wombat", "Digger"),
    ("wedge_tail_eagle", "Aria"),
    ("goanna", "Rex"),
]


def apply_luminara_starter_scenario(zoo: Zoo) -> str:
    """Credit funds and adopt the canonical seven-resident roster.

    Matches the names and species listed in the Luminara / OzZoo tutorial draft.
    Safe to call on an empty or partially filled zoo; may raise if at capacity
    or funds insufficient after prior spending.
    """
    bal = zoo.treasury.balance
    if bal < LUMINARA_STARTER_FUNDS:
        zoo.treasury.credit(LUMINARA_STARTER_FUNDS - bal, context="luminara_starter_seed")
    for species_key, name in _STARTER_ADOPTIONS:
        zoo.adopt_species(species_key, name)
    return (
        f"Luminara starter loaded: ${LUMINARA_STARTER_FUNDS:,.0f} target balance, "
        f"{len(_STARTER_ADOPTIONS)} residents adopted."
    )
