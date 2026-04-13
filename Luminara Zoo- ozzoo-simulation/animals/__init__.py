"""Australian wildlife taxa for the Luminara Zoo simulation."""

from animals.animal import Animal
from animals.bird import Bird, Emu, WedgeTailEagle
from animals.canid import Canidae, Dingo
from animals.factory import AnimalFactory, AnimalFactoryError
from animals.interfaces import IBreedable, ICleanable, IObserver
from animals.marsupial import Kangaroo, Koala, Marsupial, Wombat
from animals.reptile import Goanna, Reptile

__all__ = [
    "Animal",
    "AnimalFactory",
    "AnimalFactoryError",
    "Bird",
    "Canidae",
    "Dingo",
    "Emu",
    "Goanna",
    "IBreedable",
    "ICleanable",
    "IObserver",
    "Kangaroo",
    "Koala",
    "Marsupial",
    "Reptile",
    "WedgeTailEagle",
    "Wombat",
]
