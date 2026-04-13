"""Avian branch: flight-capable and cursorial Australian birds."""

from __future__ import annotations

from typing import Any

from animals.animal import Animal
from animals.interfaces import IBreedable, ICleanable
from systems.exceptions import FeedingError


class Bird(Animal):
    """Intermediate taxon for birds under zoo husbandry."""

    def __init__(
        self,
        *,
        name: str,
        health: int = 80,
        hunger: int = 42,
        cleanliness: int = 68,
        happiness: int = 73,
    ) -> None:
        """Create a bird with baseline metrics for active metabolism."""
        super().__init__(
            name=name,
            health=health,
            hunger=hunger,
            cleanliness=cleanliness,
            happiness=happiness,
        )

    @property
    def family(self) -> str:
        return "Bird"


class Emu(Bird, IBreedable, ICleanable):
    """Large ratite omnivore with strong foraging drive."""

    def make_sound(self) -> str:
        return "Deep drumming boom from the chest cavity."

    def get_dietary_needs(self) -> dict[str, Any]:
        return {
            "species": "Emu",
            "acceptable_foods": ("grain", "greens", "insects", "fruit"),
            "staple": "grain",
            "notes": "Grit and calcium for digestion; wide-ranging walk.",
        }

    def eat(self, food_offered: str) -> str:
        token = food_offered.lower().strip()
        acceptable = {"grain", "greens", "insects", "fruit"}
        if token not in acceptable:
            raise FeedingError(
                f"Emus decline '{food_offered}'. Offer grain, greens, insects, or fruit."
            )
        self.hunger = max(0, self.hunger - 32)
        self.health = min(100, self.health + 2)
        self.reward_feeding()
        return f"{self.name} pecks enthusiastically at {token} along the fence line."

    def can_breed(self) -> bool:
        return (
            self.is_alive
            and self.health >= 57
            and self.hunger <= 66
            and self.happiness >= 54
        )

    def describe_breeding_plan(self) -> str:
        if self.can_breed():
            return "Nest pad prepared; seasonal pairing authorised."
        return "Hold eggs: stabilise micronutrients and reduce visitor pressure."

    def needs_cleaning(self) -> bool:
        return self.cleanliness < 46

    def clean(self) -> str:
        self.cleanliness = min(100, self.cleanliness + 34)
        return f"{self.name}'s paddock harrowed; dust bath refilled."


class WedgeTailEagle(Bird, IBreedable, ICleanable):
    """Large raptor requiring elevated perches and whole prey."""

    def make_sound(self) -> str:
        return "Piercing whistle escalating to a whistling kite-like cry."

    def get_dietary_needs(self) -> dict[str, Any]:
        return {
            "species": "Wedge-tailed Eagle",
            "acceptable_foods": ("meat", "carcass", "prey"),
            "staple": "meat",
            "notes": "Carcass tethering for natural tearing behaviours.",
        }

    def eat(self, food_offered: str) -> str:
        token = food_offered.lower().strip()
        acceptable = {"meat", "carcass", "prey"}
        if token not in acceptable:
            raise FeedingError(
                f"Wedge-tails reject '{food_offered}'. Provide meat, carcass, or prey items."
            )
        self.hunger = max(0, self.hunger - 38)
        self.health = min(100, self.health + 3)
        self.reward_feeding()
        return f"{self.name} mantles over {token} on the high platform."

    def can_breed(self) -> bool:
        return (
            self.is_alive
            and self.health >= 70
            and self.hunger <= 55
            and self.happiness >= 60
        )

    def describe_breeding_plan(self) -> str:
        if self.can_breed():
            return "Raptor team may proceed with formal studbook pairing."
        return "No breeding this cycle: improve body score and flight fitness."

    def needs_cleaning(self) -> bool:
        return self.cleanliness < 44

    def clean(self) -> str:
        self.cleanliness = min(100, self.cleanliness + 33)
        return f"{self.name}'s mews pressure-washed; glove kit rotated."
