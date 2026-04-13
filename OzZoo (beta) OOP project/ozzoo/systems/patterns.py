"""
systems/patterns.py — Observer, Factory, and Resource classes for OzZoo.

Design patterns implemented
----------------------------
1. **Observer Pattern** (Gang of Four Behavioural)
   EventBus is the subject; any object that implements IObserver can
   subscribe.  When an animal's health goes critical the EventBus fires
   a HEALTH_CRITICAL event and all subscribed observers (e.g. the CLI
   dashboard) are notified — without the Animal class needing to know
   about the UI layer.

   Reference:
       Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994).
       *Design patterns: Elements of reusable object-oriented software*.
       Addison-Wesley.

2. **Factory Pattern** (Gang of Four Creational)
   AnimalFactory.create(species_name, individual_name) returns the
   correct concrete Animal subclass without the caller needing to import
   every species module.  Adding a new species requires only adding one
   entry to the registry — no changes to client code.

3. **Singleton Pattern** (Gang of Four Creational)
   FoodStore and MedicineStore are Singletons — the zoo has exactly one
   pantry and one vet cabinet, ensuring all parts of the game read and
   write the same inventory.

Author : Babatundji Williams-Fulwood
Student ID : s8138393
Unit : NIT2112 Object Oriented Programming — Victoria University
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from animals.base import (
    Animal,
    Koala, Kangaroo, Wombat,
    Dingo,
    Emu, WedgeTailEagle,
    Goanna,
)
from systems.exceptions import (
    InsufficientFoodError,
    InsufficientMedicineError,
    InsufficientFundsError,
)


# ===========================================================================
# Observer Pattern
# ===========================================================================

class IObserver(ABC):
    """
    Observer interface — concrete observers must implement on_event().

    Any class wishing to receive zoo events (health alerts, weather events,
    visitor milestones) should implement this interface and register itself
    with the EventBus.
    """

    @abstractmethod
    def on_event(self, event_type: str, payload: dict) -> None:
        """
        Receive and process a zoo event.

        Args:
            event_type (str): Identifier such as 'HEALTH_CRITICAL'.
            payload    (dict): Event-specific data (animal name, value, etc.).
        """


class EventBus:
    """
    Singleton event dispatcher (Subject in Observer pattern).

    The EventBus maintains a list of observers keyed by event type.
    Any subsystem can call publish() to notify all interested parties.

    Usage:
        bus = EventBus.get_instance()
        bus.subscribe("HEALTH_CRITICAL", my_observer)
        bus.publish("HEALTH_CRITICAL", {"animal": "Bindi", "health": 15.0})
    """

    _instance: "EventBus | None" = None
    _event_log: list[dict] = []

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._observers: dict[str, list[IObserver]] = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "EventBus":
        """Return the singleton EventBus instance."""
        return cls()

    def subscribe(self, event_type: str, observer: IObserver) -> None:
        """
        Register *observer* to receive events of *event_type*.

        Args:
            event_type (str):      Event identifier to listen for.
            observer   (IObserver): The observer to register.
        """
        self._observers.setdefault(event_type, []).append(observer)

    def unsubscribe(self, event_type: str, observer: IObserver) -> None:
        """Deregister *observer* from *event_type* notifications."""
        if event_type in self._observers:
            self._observers[event_type] = [
                o for o in self._observers[event_type] if o is not observer
            ]

    def publish(self, event_type: str, payload: dict) -> None:
        """
        Broadcast an event to all registered observers.

        Args:
            event_type (str):  Event identifier.
            payload    (dict): Event-specific data.
        """
        self._event_log.append({"type": event_type, "payload": payload})
        for observer in self._observers.get(event_type, []):
            observer.on_event(event_type, payload)

    def get_log(self) -> list[dict]:
        """Return a copy of all events published this session."""
        return list(self._event_log)


# ===========================================================================
# Factory Pattern — AnimalFactory
# ===========================================================================

# Registry maps lower-case species name → concrete class
_SPECIES_REGISTRY: dict[str, type[Animal]] = {
    "koala":               Koala,
    "eastern grey kangaroo": Kangaroo,
    "kangaroo":            Kangaroo,
    "common wombat":       Wombat,
    "wombat":              Wombat,
    "dingo":               Dingo,
    "emu":                 Emu,
    "wedge-tailed eagle":  WedgeTailEagle,
    "wedge tail eagle":    WedgeTailEagle,
    "eagle":               WedgeTailEagle,
    "lace monitor (goanna)": Goanna,
    "goanna":              Goanna,
}


class AnimalFactory:
    """
    Factory class that creates Animal objects by species name.

    Decouples object creation from the rest of the game — callers never
    need to import individual animal modules.

    Reference:
        Gamma et al. (1994) refer to this as the *Factory Method* pattern,
        where object creation logic is encapsulated in a dedicated class.
    """

    @staticmethod
    def create(species_name: str, individual_name: str) -> Animal:
        """
        Instantiate and return a concrete Animal of the requested species.

        Args:
            species_name    (str): Common name of the species (case-insensitive).
            individual_name (str): The animal's display name (e.g. "Bindi").

        Returns:
            A fully initialised Animal subclass instance.

        Raises:
            ValueError: If species_name is not in the registry.
        """
        key = species_name.strip().lower()
        cls = _SPECIES_REGISTRY.get(key)
        if cls is None:
            available = ", ".join(sorted({k.title() for k in _SPECIES_REGISTRY}))
            raise ValueError(
                f"Unknown species '{species_name}'. "
                f"Available species: {available}."
            )
        return cls(individual_name)

    @staticmethod
    def available_species() -> list[str]:
        """Return a deduplicated, title-cased list of purchasable species."""
        seen: set[str] = set()
        result: list[str] = []
        for cls in _SPECIES_REGISTRY.values():
            # Use a temporary instance to read the species property.
            temp = cls("_")
            label = temp.species
            if label not in seen:
                seen.add(label)
                result.append(label)
        return sorted(result)

    @staticmethod
    def get_price(species_name: str) -> float:
        """Return the purchase price for a species without instantiating it."""
        key = species_name.strip().lower()
        cls = _SPECIES_REGISTRY.get(key)
        if cls is None:
            raise ValueError(f"Unknown species '{species_name}'.")
        return cls("_").purchase_price


# ===========================================================================
# Singleton — FoodStore
# ===========================================================================

class FoodStore:
    """
    Singleton inventory of all food types held by OzZoo.

    Maintains stock levels and deducts quantities when animals are fed.
    All food purchases add to this single shared inventory.

    Stock is measured in kilograms (kg).
    """

    _instance: "FoodStore | None" = None

    # Prices per kg (AUD)
    FOOD_PRICES: dict[str, float] = {
        "Eucalyptus": 4.50,
        "Grass":      1.20,
        "Hay":        0.80,
        "Seeds":      2.00,
        "Insects":    6.00,
        "Raw Meat":   8.00,
        "Bone":       3.00,
        "Roots":      1.50,
        "Eggs":       5.00,
    }

    def __new__(cls) -> "FoodStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialise with a small starter stock.
            cls._instance._stock: dict[str, float] = {
                ft: 10.0 for ft in cls.FOOD_PRICES
            }
        return cls._instance

    @classmethod
    def get_instance(cls) -> "FoodStore":
        return cls()

    def stock(self) -> dict[str, float]:
        """Return a copy of the current stock levels."""
        return dict(self._stock)

    def purchase(self, food_type: str, kg: float, treasury: "Treasury") -> str:
        """
        Buy *kg* kilograms of *food_type* and charge *treasury*.

        Args:
            food_type (str):      Food variety to purchase.
            kg        (float):    Kilograms to buy.
            treasury  (Treasury): The zoo's financial account to debit.

        Returns:
            A confirmation string.

        Raises:
            ValueError:            If food_type is not in the catalogue.
            InsufficientFundsError: If the treasury cannot cover the cost.
        """
        if food_type not in self.FOOD_PRICES:
            raise ValueError(f"'{food_type}' is not a recognised food type.")
        cost = self.FOOD_PRICES[food_type] * kg
        treasury.debit(cost, f"Food purchase: {kg:.1f} kg {food_type}")
        self._stock[food_type] = self._stock.get(food_type, 0.0) + kg
        return (
            f"🛒 Purchased {kg:.1f} kg of {food_type} for ${cost:,.2f}. "
            f"New stock: {self._stock[food_type]:.1f} kg."
        )

    def consume(self, food_type: str, kg: float) -> None:
        """
        Deduct *kg* from stock when feeding an animal.

        Raises:
            InsufficientFoodError: If the deduction would make stock negative.
        """
        available = self._stock.get(food_type, 0.0)
        if available < kg:
            raise InsufficientFoodError(food_type, kg, available)
        self._stock[food_type] = available - kg


# ===========================================================================
# Singleton — MedicineStore
# ===========================================================================

class MedicineStore:
    """
    Singleton veterinary cabinet for OzZoo.

    Stores medicine doses.  Each treatment costs one dose.
    """

    _instance: "MedicineStore | None" = None

    MEDICINE_PRICES: dict[str, float] = {
        "General Antibiotic": 50.00,
        "Antifungal":        75.00,
        "Wound Salve":       30.00,
        "Vitamin Supplement": 20.00,
    }

    def __new__(cls) -> "MedicineStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._doses: dict[str, int] = {
                med: 5 for med in cls.MEDICINE_PRICES
            }
        return cls._instance

    @classmethod
    def get_instance(cls) -> "MedicineStore":
        return cls()

    def doses(self) -> dict[str, int]:
        """Return a copy of current dose counts."""
        return dict(self._doses)

    def purchase(self, medicine: str, qty: int, treasury: "Treasury") -> str:
        """Buy *qty* doses of *medicine*."""
        if medicine not in self.MEDICINE_PRICES:
            raise ValueError(f"'{medicine}' is not stocked.")
        cost = self.MEDICINE_PRICES[medicine] * qty
        treasury.debit(cost, f"Medicine purchase: {qty}x {medicine}")
        self._doses[medicine] = self._doses.get(medicine, 0) + qty
        return f"💊 Purchased {qty}x {medicine} for ${cost:,.2f}."

    def use(self, medicine: str) -> None:
        """Use one dose of *medicine*."""
        if self._doses.get(medicine, 0) < 1:
            raise InsufficientMedicineError(medicine)
        self._doses[medicine] -= 1


# ===========================================================================
# Treasury (tracks finances)
# ===========================================================================

@dataclass
class Transaction:
    """Single financial record stored in the Treasury ledger."""
    description: str
    amount: float      # positive = credit, negative = debit
    day: int


class Treasury:
    """
    Manages the zoo's financial accounts.

    Tracks a running balance and maintains a ledger of all transactions
    so the manager can review income and expenditure.
    """

    def __init__(self, starting_balance: float = 50_000.00) -> None:
        self._balance: float = starting_balance
        self._ledger: list[Transaction] = []
        self._day: int = 1

    @property
    def balance(self) -> float:
        """Current account balance (AUD)."""
        return self._balance

    def set_day(self, day: int) -> None:
        """Sync treasury's day counter with the game loop."""
        self._day = day

    def credit(self, amount: float, description: str) -> None:
        """Add *amount* to the balance."""
        self._balance += amount
        self._ledger.append(Transaction(description, amount, self._day))

    def debit(self, amount: float, description: str) -> None:
        """
        Deduct *amount* from the balance.

        Raises:
            InsufficientFundsError: If the balance would go negative.
        """
        if amount > self._balance:
            raise InsufficientFundsError(amount, self._balance)
        self._balance -= amount
        self._ledger.append(Transaction(description, -amount, self._day))

    def get_ledger(self) -> list[Transaction]:
        """Return all recorded transactions."""
        return list(self._ledger)

    def summary(self) -> str:
        """One-line financial summary."""
        total_income = sum(t.amount for t in self._ledger if t.amount > 0)
        total_expenses = sum(-t.amount for t in self._ledger if t.amount < 0)
        return (
            f"Balance: ${self._balance:,.2f} | "
            f"Income: ${total_income:,.2f} | "
            f"Expenses: ${total_expenses:,.2f}"
        )
