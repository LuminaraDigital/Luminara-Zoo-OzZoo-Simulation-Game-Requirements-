"""Observer pattern: decouple welfare alerts from UI (Gamma et al., 1994)."""

from __future__ import annotations

from typing import Any, List

from animals.interfaces import IObserver


class EventBus:
    """Collects ``IObserver`` subscribers and broadcasts typed domain events."""

    def __init__(self) -> None:
        self.__subscribers: List[IObserver] = []

    def subscribe(self, observer: IObserver) -> None:
        """Register a listener if not already present."""
        if observer not in self.__subscribers:
            self.__subscribers.append(observer)

    def unsubscribe(self, observer: IObserver) -> None:
        """Remove a listener."""
        try:
            self.__subscribers.remove(observer)
        except ValueError:
            pass

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Notify all subscribers (errors in one observer do not block others)."""
        for obs in list(self.__subscribers):
            try:
                obs.on_event(event_type, payload)
            except Exception:  # pragma: no cover - keep simulation running
                continue
