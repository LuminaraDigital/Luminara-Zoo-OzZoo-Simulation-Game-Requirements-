"""Abstract base class for all Luminara Zoo animals."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


def _clamp_metric(value: float | int) -> int:
    """Clamp a percentage-style metric into ``[0, 100]`` as an integer."""
    try:
        v = int(round(float(value)))
    except (TypeError, ValueError):
        v = 0
    return max(0, min(100, v))


class Animal(ABC):
    """Abstract animal with encapsulated welfare metrics.

    Subclasses implement species-specific behaviour via ``make_sound``,
    ``get_dietary_needs``, and ``eat``. Callers should reference this base type
    when feeding so polymorphism applies uniformly (Gamma et al., 1994).
    """

    def __init__(
        self,
        *,
        name: str,
        health: int = 80,
        hunger: int = 40,
        cleanliness: int = 70,
        happiness: int = 72,
    ) -> None:
        """Initialize common welfare fields with validation.

        Args:
            name: Keeper-facing individual name.
            health: Initial health percentage.
            hunger: Initial hunger percentage (higher = hungrier).
            cleanliness: Initial enclosure or coat cleanliness percentage.
            happiness: Mood / enrichment satisfaction percentage.
        """
        self.__name = self._validate_name(name)
        self.__is_alive = True
        self.health = health
        self.hunger = hunger
        self.cleanliness = cleanliness
        self.happiness = happiness

    @staticmethod
    def _validate_name(name: str) -> str:
        """Ensure ``name`` is a non-empty string."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Animal name must be a non-empty string.")
        return name.strip()

    @property
    @abstractmethod
    def family(self) -> str:
        """High-level husbandry family used for habitat compatibility checks."""

    @property
    def name(self) -> str:
        """Individual name shown in UI and logs."""
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = self._validate_name(value)

    @property
    def is_alive(self) -> bool:
        """False once welfare has collapsed to death (removed from zoo on tick)."""
        return self.__is_alive

    @property
    def health(self) -> int:
        """Health percentage in ``[0, 100]``."""
        return self.__health

    @health.setter
    def health(self, value: float | int) -> None:
        self.__health = _clamp_metric(value)
        if self.__health <= 0:
            self.__is_alive = False

    @property
    def hunger(self) -> int:
        """Hunger percentage in ``[0, 100]`` (higher means needs food sooner)."""
        return self.__hunger

    @hunger.setter
    def hunger(self, value: float | int) -> None:
        self.__hunger = _clamp_metric(value)

    @property
    def cleanliness(self) -> int:
        """Cleanliness percentage in ``[0, 100]``."""
        return self.__cleanliness

    @cleanliness.setter
    def cleanliness(self, value: float | int) -> None:
        self.__cleanliness = _clamp_metric(value)

    @property
    def happiness(self) -> int:
        """Happiness / enrichment percentage in ``[0, 100]``."""
        return self.__happiness

    @happiness.setter
    def happiness(self, value: float | int) -> None:
        self.__happiness = _clamp_metric(value)

    def apply_daily_stress(self, *, heatwave: bool = False) -> None:
        """Advance hunger and welfare decay for one simulation day.

        Args:
            heatwave: If True, apply extra thermal stress (special event).
        """
        if not self.__is_alive:
            return
        self.hunger = min(100, self.hunger + 8)
        self.cleanliness = max(0, self.cleanliness - 3)
        if heatwave:
            self.health = max(0, self.health - 5)
            self.happiness = max(0, self.happiness - 8)
        if self.hunger > 80:
            self.happiness = max(0, self.happiness - 4)
        if self.hunger > 92:
            self.health = max(0, self.health - 7)
        if self.cleanliness < 28:
            self.health = max(0, self.health - 3)
            self.happiness = max(0, self.happiness - 3)
        if self.health < 25:
            self.happiness = max(0, self.happiness - 5)

    def revive_health_floor(self) -> None:
        """Internal: after medicine, ensure alive flag if health restored."""
        if self.__health > 0:
            self.__is_alive = True

    def reward_feeding(self) -> None:
        """Boost mood after a successful meal (called from concrete ``eat``)."""
        if self.__is_alive:
            self.happiness = min(100, self.happiness + 5)

    def apply_medicine(self, *, health_boost: int = 22, mood_boost: int = 6) -> str:
        """Veterinary care: improve health and happiness when alive.

        Args:
            health_boost: Points added to health (clamped).
            mood_boost: Points added to happiness (clamped).

        Returns:
            A short log line for the CLI.
        """
        if not self.__is_alive:
            return f"{self.name} cannot receive medicine — already deceased."
        self.health = min(100, self.health + health_boost)
        self.happiness = min(100, self.happiness + mood_boost)
        self.revive_health_floor()
        return f"{self.name} receives treatment and settles calmly."

    @abstractmethod
    def make_sound(self) -> str:
        """Return an onomatopoeic or descriptive vocalisation string."""

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, Any]:
        """Describe accepted foods and rough daily needs for keepers."""

    @abstractmethod
    def eat(self, food_offered: str) -> str:
        """Consume offered food, update hunger/health, and return a log line.

        Args:
            food_offered: Normalised food token (e.g. ``"eucalyptus"``).

        Returns:
            Short message suitable for game logs.
        """

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        cls_name = self.__class__.__name__
        return (
            f"{cls_name}(name={self.name!r}, health={self.health}, "
            f"hunger={self.hunger}, happy={self.happiness})"
        )
