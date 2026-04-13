"""Reptile branch: monitor lizard representative species."""

from __future__ import annotations

from typing import Any

from animals.animal import Animal
from animals.interfaces import IBreedable, ICleanable
from systems.exceptions import FeedingError


class Reptile(Animal):
    """Intermediate taxon for ectothermic species with thermal gradients."""

    def __init__(
        self,
        *,
        name: str,
        health: int = 78,
        hunger: int = 35,
        cleanliness: int = 60,
        happiness: int = 68,
    ) -> None:
        """Create a reptile with baselines reflecting slower metabolism."""
        super().__init__(
            name=name,
            health=health,
            hunger=hunger,
            cleanliness=cleanliness,
            happiness=happiness,
        )

    @property
    def family(self) -> str:
        return "Reptile"


class Goanna(Reptile, IBreedable, ICleanable):
    """Large varanid with climbing and digging enrichment needs."""

    def make_sound(self) -> str:
        return "Hiss and sharp exhale; mostly silent ambush predator."

    def get_dietary_needs(self) -> dict[str, Any]:
        return {
            "species": "Goanna",
            "acceptable_foods": ("insects", "eggs", "meat", "carcass"),
            "staple": "insects",
            "notes": "Calcium-dusted invertebrates; occasional vertebrate prey.",
        }

    def eat(self, food_offered: str) -> str:
        token = food_offered.lower().strip()
        acceptable = {"insects", "eggs", "meat", "carcass"}
        if token not in acceptable:
            raise FeedingError(
                f"Goannas refuse '{food_offered}'. Try insects, eggs, meat, or carcass."
            )
        self.hunger = max(0, self.hunger - 25)
        self.health = min(100, self.health + 2)
        self.reward_feeding()
        return f"{self.name} snaps up {token} from the tongs, tail coiled."

    def can_breed(self) -> bool:
        return False

    def describe_breeding_plan(self) -> str:
        return "Breeding not scheduled for this individual this assessment cycle."

    def needs_cleaning(self) -> bool:
        return self.cleanliness < 52

    def clean(self) -> str:
        self.cleanliness = min(100, self.cleanliness + 30)
        return f"{self.name}'s hot rock scrubbed; mulch layer replaced."
