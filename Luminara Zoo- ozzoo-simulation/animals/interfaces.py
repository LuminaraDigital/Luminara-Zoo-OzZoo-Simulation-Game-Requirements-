"""Protocol-style ABC interfaces for cross-cutting capabilities.

References:
    Gamma et al. (1994); Martin (2017).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IBreedable(ABC):
    """Interface for animals that may reproduce under managed conditions."""

    @abstractmethod
    def can_breed(self) -> bool:
        """Return True if the individual is currently able to breed."""

    @abstractmethod
    def describe_breeding_plan(self) -> str:
        """Return a short natural-language breeding status for keepers."""


class ICleanable(ABC):
    """Interface for entities whose hygiene or enclosure state must be managed."""

    @abstractmethod
    def needs_cleaning(self) -> bool:
        """Return True if cleaning should be scheduled soon."""

    @abstractmethod
    def clean(self) -> str:
        """Perform a cleaning cycle and return a keeper-facing log line."""


class IObserver(ABC):
    """Observer interface for the publish/subscribe welfare alert system."""

    @abstractmethod
    def on_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """React to a domain event raised by the ``EventBus``.

        Args:
            event_type: Short label such as ``"critical_health"``.
            payload: Structured context (animal name, metrics, day).
        """
