"""Factory pattern for constructing species from string keys (Gamma et al., 1994)."""

from __future__ import annotations

from typing import Callable, Dict, Type

from animals.animal import Animal
from animals.bird import Emu, WedgeTailEagle
from animals.canid import Dingo
from animals.marsupial import Kangaroo, Koala, Wombat
from animals.reptile import Goanna
from systems.exceptions import OzZooBaseException


class AnimalFactoryError(OzZooBaseException):
    """Raised when a species key cannot be mapped to a concrete class."""

    pass


class AnimalFactory:
    """Builds ``Animal`` instances without exposing constructors to the CLI."""

    _registry: Dict[str, Type[Animal]] = {
        "koala": Koala,
        "kangaroo": Kangaroo,
        "wombat": Wombat,
        "dingo": Dingo,
        "emu": Emu,
        "wedge_tail_eagle": WedgeTailEagle,
        "wedgetaileagle": WedgeTailEagle,
        "eagle": WedgeTailEagle,
        "goanna": Goanna,
    }

    _pricing: Dict[str, float] = {
        "koala": 4200.0,
        "kangaroo": 3100.0,
        "wombat": 2800.0,
        "dingo": 3600.0,
        "emu": 2200.0,
        "wedge_tail_eagle": 8900.0,
        "wedgetaileagle": 8900.0,
        "eagle": 8900.0,
        "goanna": 1900.0,
    }

    @classmethod
    def normalise_key(cls, species_key: str) -> str:
        """Normalise user or CLI input to a registry key."""
        k = species_key.lower().strip().replace("-", "_").replace(" ", "_")
        if k in {"wedge", "wedge_tailed_eagle"}:
            return "wedge_tail_eagle"
        return k

    @classmethod
    def supported_species(cls) -> Dict[str, Type[Animal]]:
        """Canonical creatable species keys for menus and documentation."""
        return {
            "koala": Koala,
            "kangaroo": Kangaroo,
            "wombat": Wombat,
            "dingo": Dingo,
            "emu": Emu,
            "wedge_tail_eagle": WedgeTailEagle,
            "goanna": Goanna,
        }

    @classmethod
    def adoption_price(cls, species_key: str) -> float:
        """Default acquisition cost in AUD."""
        key = cls.normalise_key(species_key)
        if key not in cls._pricing:
            raise AnimalFactoryError(f"No price list entry for '{species_key}'.")
        return cls._pricing[key]

    @classmethod
    def create(cls, species_key: str, *, name: str) -> Animal:
        """Instantiate a species implementation.

        Raises:
            AnimalFactoryError: Unknown ``species_key``.
        """
        key = cls.normalise_key(species_key)
        ctor: Callable[..., Animal] | None = cls._registry.get(key)
        if ctor is None:
            raise AnimalFactoryError(
                f"Unknown species '{species_key}'. "
                f"Try one of: {', '.join(sorted(set(cls._registry.keys()) - {'wedgetaileagle', 'eagle'}))}."
            )
        return ctor(name=name)
