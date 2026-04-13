"""Ecological zone façade grouping one or more enclosures (Tutorial: Habitat)."""

from __future__ import annotations

from typing import List, Optional

from zoo.enclosure import Enclosure


class Habitat:
    """Named ecological zone that contains one or more ``Enclosure`` parcels.

    This is a thin façade: all assignment rules remain on ``Enclosure``; the
    habitat exists so documentation can speak of "Bushlands" containing both
    marsupial yards without duplicating compatibility logic.
    """

    def __init__(self, zone_name: str, enclosures: List[Enclosure]) -> None:
        if not zone_name.strip():
            raise ValueError("Habitat zone name required.")
        if not enclosures:
            raise ValueError("A habitat must contain at least one enclosure.")
        self.__zone_name = zone_name.strip()
        self.__enclosures = list(enclosures)

    @property
    def zone_name(self) -> str:
        return self.__zone_name

    @property
    def enclosures(self) -> List[Enclosure]:
        return list(self.__enclosures)

    def describe(self) -> str:
        """Single line for status screens and Tutorial-style reporting."""
        inner = " | ".join(e.describe() for e in self.__enclosures)
        return f"{self.__zone_name}: {inner}"

    def find_enclosure(self, label: str) -> Optional[Enclosure]:
        """Return a child enclosure by label (case-insensitive) or None."""
        key = label.strip().lower()
        for enc in self.__enclosures:
            if enc.label.lower() == key:
                return enc
        return None
