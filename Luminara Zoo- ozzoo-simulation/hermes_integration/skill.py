"""Hermes-oriented management API for Luminara Zoo (callable skills surface).

This module exposes **plain Python functions** with natural-language docstrings so
they can be wrapped as tools or Agent Skills for `hermes-agent`. The simulation
core stays importable even when Hermes is not installed.

Upstream runtime (install separately):

    https://github.com/NousResearch/hermes-agent.git

Install examples (from the Luminara Zoo project root)::

    pip install -r requirements-hermes.txt
    pip install -e ".[hermes]"

Hermes documents skills and tooling in its user guide; the Agent Skills open
format is described at https://agentskills.io/ (Anthropic et al., open standard).

References:
    Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns:
    Elements of reusable object-oriented software*. Addison-Wesley.
    Martin, R. C. (2017). *Clean architecture: A craftsman's guide to software
    structure and design*. Prentice Hall.
    Nous Research. (n.d.). *Hermes Agent* [Computer software]. GitHub.
    https://github.com/NousResearch/hermes-agent
"""

from __future__ import annotations

from typing import Any

from systems.exceptions import AnimalNotFoundError
from zoo.zoo import Zoo

__all__ = [
    "SKILL_SOURCE_URL",
    "advance_day",
    "feed_animal",
    "get_zoo_status",
]

# Canonical upstream URL (assessment traceability).
SKILL_SOURCE_URL = "https://github.com/NousResearch/hermes-agent.git"


def get_zoo_status() -> dict[str, Any]:
    """Return a JSON-serialisable snapshot of the zoo for managers and agents.

    Use when the operator asks for an overview, census, funds, or welfare
    summary. Reads the process-wide ``Zoo`` singleton (population, capacity,
    treasury balance, habitats, pantry, per-animal health, hunger,
    cleanliness, and happiness).
    """
    return Zoo().get_zoo_status()


def feed_animal(animal_name: str, food_offered: str, meal_cost: float = 12.5) -> str:
    """Prepare a meal, charge the treasury, and feed one resident by name.

    Use when the operator says to feed, offer food to, or serve a diet to a
    named animal. The name match is case-insensitive. ``food_offered`` must be
    a token the species accepts (for example ``eucalyptus`` for koalas or
    ``meat`` for dingoes). ``meal_cost`` is in AUD and debits the singleton
    treasury before calling the polymorphic ``eat`` implementation.

    Args:
        animal_name: Resident display name (e.g. "Bunyip").
        food_offered: Food keyword understood by that species.
        meal_cost: Dollar cost deducted before feeding; must be positive.

    Returns:
        A short log line produced by the animal's ``eat`` method.

    Raises:
        AnimalNotFoundError: If no resident matches ``animal_name``.
        systems.exceptions.InsufficientFundsError: If the treasury cannot pay.
        systems.exceptions.FeedingError: If the diet is rejected (meal cost is
            rolled back by ``Zoo.feed_animal``).
    """
    zoo = Zoo()
    key = animal_name.strip().lower()
    for candidate in zoo.list_animals():
        if candidate.name.strip().lower() == key:
            return zoo.feed_animal(candidate, food_offered, meal_cost)
    raise AnimalNotFoundError(f"No resident named {animal_name!r}.")


def advance_day() -> dict[str, Any]:
    """Run the full simulation day tick on the ``Zoo`` singleton.

    Use when the operator asks to end the day, run overnight processing, or move
    to tomorrow. This applies hunger and welfare decay, optional heatwave stress,
    visitor admissions revenue tied to satisfaction, celebration donations,
    ``EventBus`` alerts for critical health and deaths, and removes deceased
    animals from the census.
    """
    return Zoo().advance_day()
