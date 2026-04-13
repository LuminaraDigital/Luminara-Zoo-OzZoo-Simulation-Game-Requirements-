"""Marsupial branch: intermediate class and concrete Australian species."""

from __future__ import annotations

from typing import Any

from animals.animal import Animal
from animals.interfaces import IBreedable, ICleanable
from systems.exceptions import FeedingError


class Marsupial(Animal):
    """Intermediate taxon for pouched mammals native to Australia."""

    def __init__(
        self,
        *,
        name: str,
        health: int = 82,
        hunger: int = 38,
        cleanliness: int = 72,
        happiness: int = 74,
    ) -> None:
        """Create a marsupial with slightly adjusted default welfare baselines."""
        super().__init__(
            name=name,
            health=health,
            hunger=hunger,
            cleanliness=cleanliness,
            happiness=happiness,
        )

    @property
    def family(self) -> str:
        return "Marsupial"


class Koala(Marsupial, IBreedable, ICleanable):
    """Folivorous marsupial specialising in eucalyptus browse."""

    def make_sound(self) -> str:
        return "Grunting bellow and nasal snuffle."

    def get_dietary_needs(self) -> dict[str, Any]:
        return {
            "species": "Koala",
            "acceptable_foods": ("eucalyptus", "browse"),
            "staple": "eucalyptus",
            "notes": "Low-energy foliage; frequent short feeds.",
        }

    def eat(self, food_offered: str) -> str:
        token = food_offered.lower().strip()
        acceptable = {"eucalyptus", "browse"}
        if token not in acceptable:
            raise FeedingError(f"Koalas reject '{food_offered}'. Offer eucalyptus or browse.")
        self.hunger = max(0, self.hunger - 35)
        self.health = min(100, self.health + 2)
        self.reward_feeding()
        return f"{self.name} chews {token} calmly in the fork of a gum."

    def can_breed(self) -> bool:
        return (
            self.is_alive
            and self.health >= 55
            and self.hunger <= 70
            and self.happiness >= 52
        )

    def describe_breeding_plan(self) -> str:
        if self.can_breed():
            return "Joey development can proceed with vet clearance."
        return "Defer breeding until health improves and hunger stabilises."

    def needs_cleaning(self) -> bool:
        return self.cleanliness < 45

    def clean(self) -> str:
        self.cleanliness = min(100, self.cleanliness + 40)
        return f"{self.name}'s perch and browse bins sanitised."


class Kangaroo(Marsupial, IBreedable, ICleanable):
    """Large macropod grazer requiring open space and roughage."""

    def make_sound(self) -> str:
        return "Thumping foot-drums and soft chuffing."

    def get_dietary_needs(self) -> dict[str, Any]:
        return {
            "species": "Kangaroo",
            "acceptable_foods": ("grass", "hay", "pellets"),
            "staple": "grass",
            "notes": "High-fibre grazing; salt lick as supplement.",
        }

    def eat(self, food_offered: str) -> str:
        token = food_offered.lower().strip()
        acceptable = {"grass", "hay", "pellets"}
        if token not in acceptable:
            raise FeedingError(
                f"Kangaroos refuse '{food_offered}'. Use grass, hay, or pellets."
            )
        self.hunger = max(0, self.hunger - 30)
        self.health = min(100, self.health + 1)
        self.reward_feeding()
        return f"{self.name} grazes on {token} across the yard."

    def can_breed(self) -> bool:
        return (
            self.is_alive
            and self.health >= 60
            and self.hunger <= 65
            and self.happiness >= 55
        )

    def describe_breeding_plan(self) -> str:
        if self.can_breed():
            return "Boomer/doe pairing viable this season with space audit."
        return "Hold breeding: adjust nutrition and reduce stressors first."

    def needs_cleaning(self) -> bool:
        return self.cleanliness < 50

    def clean(self) -> str:
        self.cleanliness = min(100, self.cleanliness + 35)
        return f"{self.name}'s yard raked; water troughs scrubbed."


class Wombat(Marsupial, IBreedable, ICleanable):
    """Burrowing grazer with dense build and stubborn temperament."""

    def make_sound(self) -> str:
        return "Low growl and irritated grunt."

    def get_dietary_needs(self) -> dict[str, Any]:
        return {
            "species": "Wombat",
            "acceptable_foods": ("grass", "roots", "hay"),
            "staple": "grass",
            "notes": "Evening feeding aligns with crepuscular activity.",
        }

    def eat(self, food_offered: str) -> str:
        token = food_offered.lower().strip()
        acceptable = {"grass", "roots", "hay"}
        if token not in acceptable:
            raise FeedingError(
                f"Wombats will not eat '{food_offered}'. Try grass, roots, or hay."
            )
        self.hunger = max(0, self.hunger - 28)
        self.health = min(100, self.health + 2)
        self.reward_feeding()
        return f"{self.name} bulldozes through a pile of {token}."

    def can_breed(self) -> bool:
        return (
            self.is_alive
            and self.health >= 58
            and self.hunger <= 68
            and self.happiness >= 50
        )

    def describe_breeding_plan(self) -> str:
        if self.can_breed():
            return "Burrow inspection OK; breeding window opens next month."
        return "Postpone breeding until burrow humidity and diet are tuned."

    def needs_cleaning(self) -> bool:
        return self.cleanliness < 48

    def clean(self) -> str:
        self.cleanliness = min(100, self.cleanliness + 38)
        return f"{self.name}'s burrow mouth cleared; bedding refreshed."
