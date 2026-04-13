"""Cross-cutting systems: exceptions, treasury, pantry, and observers."""

from systems.alert_observer import AlertObserver
from systems.award_ledger import AwardLedger
from systems.event_bus import EventBus
from systems.exceptions import (
    AnimalNotFoundError,
    BreedingFailedError,
    CapacityExceededError,
    FeedingError,
    HabitatNotFoundError,
    IncompatibleSpeciesError,
    InsufficientFoodError,
    InsufficientFundsError,
    InsufficientMedicineError,
    InvalidAmountError,
    InvalidCapacityError,
    OzZooBaseException,
)
from systems.food_item import FoodItem
from systems.food_store import FoodStore
from systems.medicine import Medicine, default_medicine_cabinet
from systems.medicine_store import MedicineStore
from systems.special_events import SpecialEvents
from systems.treasury import OzZooTreasuryOperationError, Treasury

__all__ = [
    "AlertObserver",
    "AwardLedger",
    "AnimalNotFoundError",
    "BreedingFailedError",
    "CapacityExceededError",
    "EventBus",
    "FeedingError",
    "FoodItem",
    "FoodStore",
    "HabitatNotFoundError",
    "IncompatibleSpeciesError",
    "InsufficientFoodError",
    "InsufficientFundsError",
    "InsufficientMedicineError",
    "InvalidAmountError",
    "InvalidCapacityError",
    "Medicine",
    "MedicineStore",
    "OzZooBaseException",
    "OzZooTreasuryOperationError",
    "SpecialEvents",
    "Treasury",
    "default_medicine_cabinet",
]
