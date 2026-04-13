"""Canid branch: Australian dingo as intermediate + concrete species."""

from __future__ import annotations

from typing import Any

from animals.animal import Animal
from animals.interfaces import IBreedable, ICleanable
from systems.exceptions import FeedingError


class Canidae(Animal):
    """Intermediate taxon for cursorial canids kept under managed care."""

    def __init__(
        self,
        *,
        name: str,
        health: int = 85,
        hunger: int = 45,
        cleanliness: int = 65,
        happiness: int = 70,
    ) -> None:
        """Create a canid with defaults tuned for an active predator."""
        super().__init__(
            name=name,
            health=health,
            hunger=hunger,
            cleanliness=cleanliness,
            happiness=happiness,
        )

    @property
    def family(self) -> str:
        return "Canid"


class Dingo(Canidae, IBreedable, ICleanable):
    """Apex mesopredator requiring whole-prey style nutrition and enrichment."""

    def make_sound(self) -> str:
        return "High-pitched howl tapering into a yodel."

    def get_dietary_needs(self) -> dict[str, Any]:
        return {
            "species": "Dingo",
            "acceptable_foods": ("meat", "carcass", "bones"),
            "staple": "meat",
            "notes": "Scatter feeding to reduce competition stress.",
        }

    def eat(self, food_offered: str) -> str:
        token = food_offered.lower().strip()
        acceptable = {"meat", "carcass", "bones"}
        if token not in acceptable:
            raise FeedingError(
                f"Dingoes ignore '{food_offered}'. Provide meat, carcass, or bones."
            )
        self.hunger = max(0, self.hunger - 40)
        self.health = min(100, self.health + 3)
        self.reward_feeding()
        return f"{self.name} tears into {token} behind a scent puzzle."

    def can_breed(self) -> bool:
        return (
            self.is_alive
            and self.health >= 62
            and self.hunger <= 60
            and self.happiness >= 58
        )

    def describe_breeding_plan(self) -> str:
        if self.can_breed():
            return "Pair bond stable; schedule genetic diversity review."
        return "Delay breeding until body condition and enrichment targets met."

    def needs_cleaning(self) -> bool:
        return self.cleanliness < 42

    def clean(self) -> str:
        self.cleanliness = min(100, self.cleanliness + 36)
        return f"{self.name}'s den substrate replaced; pools sanitised."
