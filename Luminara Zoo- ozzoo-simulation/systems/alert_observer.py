"""CLI-facing observer that surfaces critical welfare alerts."""

from __future__ import annotations

from typing import Any, Callable, Optional

from animals.interfaces import IObserver


class AlertObserver(IObserver):
    """Prints (or routes) manager alerts when subscribed to an ``EventBus``."""

    def __init__(self, sink: Optional[Callable[[str], None]] = None) -> None:
        """Create an observer.

        Args:
            sink: Optional callable replacing ``print`` (for tests or logging).
        """
        self.__sink = sink or print

    def on_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Format and emit a human-readable alert."""
        if event_type == "critical_health":
            name = payload.get("animal", "?")
            hp = payload.get("health", 0)
            day = payload.get("day", 0)
            msg = (
                f"[ALERT day {day}] {name} critical welfare - health {hp}%. "
                "Schedule vet check and review diet."
            )
            self.__sink(msg)
        elif event_type == "animal_death":
            name = payload.get("animal", "?")
            day = payload.get("day", 0)
            self.__sink(f"[ALERT day {day}] {name} has died from poor welfare. Review protocols.")
        elif event_type == "heatwave":
            day = payload.get("day", 0)
            self.__sink(f"[EVENT day {day}] Heatwave! Extra misting and shade deployed.")
        elif event_type == "celebration":
            day = payload.get("day", 0)
            self.__sink(f"[EVENT day {day}] Community celebration - visitors donate generously!")
