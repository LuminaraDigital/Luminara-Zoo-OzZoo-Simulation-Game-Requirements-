"""Habitat parcels with capacity and species rules (ICleanable)."""

from __future__ import annotations

from typing import AbstractSet, Optional, Set

from animals.animal import Animal
from animals.interfaces import ICleanable
from systems.exceptions import CapacityExceededError, IncompatibleSpeciesError


class Enclosure(ICleanable):
    """Physical habitat slot enforcing family compatibility and occupancy limits."""

    def __init__(
        self,
        label: str,
        max_occupants: int,
        allowed_families: AbstractSet[str],
    ) -> None:
        """Configure an enclosure.

        Args:
            label: Display name (e.g. ``Koala Korner``).
            max_occupants: Hard cap on simultaneous residents.
            allowed_families: Husbandry families permitted (e.g. ``{"Marsupial"}``).
        """
        if max_occupants <= 0:
            raise ValueError("Enclosure capacity must be positive.")
        self.__label = label.strip()
        if not self.__label:
            raise ValueError("Enclosure label required.")
        self.__max = max_occupants
        self.__allowed = frozenset(allowed_families)
        if not self.__allowed:
            raise ValueError("At least one allowed family is required.")
        self.__cleanliness = 78
        self.__occupants: Set[str] = set()

    @property
    def label(self) -> str:
        return self.__label

    @property
    def max_occupants(self) -> int:
        return self.__max

    @property
    def allowed_families(self) -> frozenset[str]:
        return self.__allowed

    @property
    def cleanliness(self) -> int:
        return self.__cleanliness

    @cleanliness.setter
    def cleanliness(self, value: int) -> None:
        self.__cleanliness = max(0, min(100, int(value)))

    def occupancy(self) -> int:
        return len(self.__occupants)

    def occupant_names(self) -> Set[str]:
        return set(self.__occupants)

    def contains(self, animal_name: str) -> bool:
        return animal_name in self.__occupants

    def try_assign(self, animal: Animal) -> None:
        """Assign ``animal`` to this enclosure or raise a domain error."""
        if animal.name in self.__occupants:
            return
        if animal.family not in self.__allowed:
            raise IncompatibleSpeciesError(
                f"{animal.name} ({animal.family}) cannot join {self.__label} — wrong habitat type.",
                family=animal.family,
                enclosure=self.__label,
            )
        if len(self.__occupants) >= self.__max:
            raise CapacityExceededError(
                f"{self.__label} is full.",
                limit=self.__max,
                attempted_total=len(self.__occupants) + 1,
            )
        self.__occupants.add(animal.name)

    def release(self, animal_name: str) -> None:
        """Remove a resident name if present."""
        self.__occupants.discard(animal_name)

    def describe(self) -> str:
        fams = ", ".join(sorted(self.__allowed))
        return (
            f"{self.__label}: {self.occupancy()}/{self.__max} animals "
            f"[{fams}] cleanliness {self.__cleanliness}%"
        )

    def needs_cleaning(self) -> bool:
        return self.__cleanliness < 50

    def clean(self) -> str:
        self.__cleanliness = min(100, self.__cleanliness + 42)
        return f"{self.__label} scrubbed and substrate refreshed."
