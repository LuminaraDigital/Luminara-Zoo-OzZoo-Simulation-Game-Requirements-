# animals/__init__.py
"""OzZoo Animals package — exposes all concrete animal classes."""
from animals.base import (
    Animal, Mammal, Marsupial, Canid, Bird, FlightlessBird, Raptor, Reptile, Monitor,
    Koala, Kangaroo, Wombat, Dingo, Emu, WedgeTailEagle, Goanna,
)
__all__ = [
    "Animal", "Mammal", "Marsupial", "Canid", "Bird", "FlightlessBird",
    "Raptor", "Reptile", "Monitor",
    "Koala", "Kangaroo", "Wombat", "Dingo", "Emu", "WedgeTailEagle", "Goanna",
]
