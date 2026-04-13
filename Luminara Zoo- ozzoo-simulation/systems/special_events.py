"""Random narrative events (creativity / playability requirement)."""

from __future__ import annotations

import random


class SpecialEvents:
    """Static helpers for stochastic day events."""

    HEATWAVE_CHANCE = 0.14
    CELEBRATION_CHANCE = 0.06

    @staticmethod
    def roll_heatwave() -> bool:
        """Return True if a heatwave stresses outdoor exhibits today."""
        return random.random() < SpecialEvents.HEATWAVE_CHANCE

    @staticmethod
    def roll_celebration() -> bool:
        """Return True if a donation-friendly celebration occurs."""
        return random.random() < SpecialEvents.CELEBRATION_CHANCE
