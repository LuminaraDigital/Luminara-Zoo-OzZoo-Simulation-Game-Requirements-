"""Veterinary consumables (assessment: Medicine entity)."""

from __future__ import annotations


class Medicine:
    """Represents a treatment option the manager can purchase and apply."""

    def __init__(
        self,
        key: str,
        label: str,
        cost_aud: float,
        health_boost: int = 24,
        mood_boost: int = 8,
    ) -> None:
        """Define a medicine SKU.

        Args:
            key: Short lookup key for menus (e.g. ``broad``).
            label: Description shown to the player.
            cost_aud: Treasury debit when applied.
            health_boost: Added to animal health (clamped by ``Animal``).
            mood_boost: Added to happiness.
        """
        self.__key = key.lower().strip()
        if not self.__key:
            raise ValueError("Medicine key required.")
        self.__label = label.strip() or self.__key
        if cost_aud <= 0:
            raise ValueError("Medicine cost must be positive.")
        self.__cost_aud = round(float(cost_aud), 2)
        self.__health_boost = int(health_boost)
        self.__mood_boost = int(mood_boost)

    @property
    def key(self) -> str:
        return self.__key

    @property
    def label(self) -> str:
        return self.__label

    @property
    def cost_aud(self) -> float:
        return self.__cost_aud

    @property
    def health_boost(self) -> int:
        return self.__health_boost

    @property
    def mood_boost(self) -> int:
        return self.__mood_boost


def default_medicine_cabinet() -> dict[str, Medicine]:
    """Return the standard treatments available in Luminara Zoo."""
    return {
        "vitamin": Medicine(
            "vitamin",
            "Vitamin supplement jab",
            35.0,
            health_boost=12,
            mood_boost=10,
        ),
        "broad": Medicine(
            "broad",
            "Broad-spectrum antibiotic course",
            120.0,
            health_boost=28,
            mood_boost=6,
        ),
        "fluid": Medicine(
            "fluid",
            "IV fluids and electrolytes",
            85.0,
            health_boost=18,
            mood_boost=12,
        ),
    }
