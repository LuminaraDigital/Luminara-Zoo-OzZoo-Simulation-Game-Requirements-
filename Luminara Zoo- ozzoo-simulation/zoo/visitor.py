"""Visitor revenue model tied to animal welfare (assessment: Visitor concept)."""

from __future__ import annotations

from typing import Any, Dict, List

from systems.treasury import Treasury


def _clamp_metric(value: float) -> int:
    return max(0, min(100, int(round(value))))


class Visitor:
    """Aggregated visitor cohort for one simulated day (headcount, satisfaction, gate revenue)."""

    def __init__(self, headcount: int, satisfaction: int, revenue_aud: float) -> None:
        """Build an immutable snapshot for logging and CLI summaries.

        Args:
            headcount: Estimated visitors admitted.
            satisfaction: Welfare-derived satisfaction percentage (0–100).
            revenue_aud: Admission revenue credited to treasury for the day.
        """
        self.__headcount = max(0, int(headcount))
        self.__satisfaction = _clamp_metric(satisfaction)
        self.__revenue_aud = max(0.0, float(revenue_aud))

    @property
    def headcount(self) -> int:
        return self.__headcount

    @property
    def satisfaction(self) -> int:
        return self.__satisfaction

    @property
    def revenue_aud(self) -> float:
        return self.__revenue_aud

    def review_blurb(self) -> str:
        """Short line suitable for newspapers or the CLI footer."""
        return (
            f"Visitors today: ~{self.__headcount} (satisfaction {self.__satisfaction}%) "
            f"— gate revenue ${self.__revenue_aud:.2f}."
        )


class VisitorDay:
    """Pure helper: derive headcount, satisfaction, and revenue from zoo welfare metrics.

    ``Zoo.advance_day`` uses this to credit the treasury without embedding visitor
    formulas in the orchestrator (single responsibility).
    """

    BASE_VISITORS = 55

    @staticmethod
    def simulate(
        animals: List[Any],
        *,
        ticket_price_aud: float,
        day: int,
        treasury: Treasury,
    ) -> Dict[str, Any]:
        """Credit treasury from ticket sales; return a summary for the UI.

        Args:
            animals: Current residents (dead animals should already be removed).
            ticket_price_aud: Price per visitor (AUD).
            day: Current simulation day (for messaging).
            treasury: Treasury to credit.

        Returns:
            Dict with visitors, revenue, satisfaction, and a log line.
        """
        alive = [a for a in animals if getattr(a, "is_alive", False)]
        if not alive:
            satisfaction = 35
        else:
            scores = []
            for a in alive:
                scores.append((a.health + a.happiness + (100 - a.hunger)) / 3)
            satisfaction = _clamp_metric(sum(scores) / len(scores))

        mood_factor = 0.55 + 0.45 * (satisfaction / 100)
        visitors = int(VisitorDay.BASE_VISITORS * mood_factor)
        revenue = round(visitors * float(ticket_price_aud), 2)

        try:
            treasury.credit(revenue, context="ticket_sales")
        except Exception:
            revenue = 0.0

        cohort = Visitor(visitors, satisfaction, revenue)
        return {
            "day": day,
            "visitors": visitors,
            "revenue_aud": revenue,
            "satisfaction": satisfaction,
            "cohort": cohort,
            "message": cohort.review_blurb(),
        }
