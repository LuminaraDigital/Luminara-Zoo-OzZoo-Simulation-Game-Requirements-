"""
zoo/entities.py — Zoo, Enclosure, Habitat, and Visitor classes for OzZoo.

ICleanable interface
---------------------
Both Enclosure and Habitat implement ICleanable, which defines the
clean() contract.  This demonstrates Python's ABC-based interface concept:
any class that promises to be cleanable must provide clean().

Singleton — Zoo
---------------
The Zoo class is a Singleton; there is precisely one zoo per game session.

Author : Babatundji Williams-Fulwood
Student ID : s8138393
Unit : NIT2112 Object Oriented Programming — Victoria University
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from systems.exceptions import (
    HabitatCapacityExceededError,
    IncompatibleSpeciesError,
    InvalidEnclosureTypeError,
)

if TYPE_CHECKING:
    from animals.base import Animal


# ===========================================================================
# ICleanable interface
# ===========================================================================

class ICleanable(ABC):
    """
    Interface defining a cleaning contract for zoo infrastructure.

    Enclosure and Habitat both implement this interface.  The concept of
    a dedicated cleaning operation models real-world zoo hygiene protocols,
    which directly affect animal health and visitor satisfaction.
    """

    @abstractmethod
    def clean(self) -> str:
        """
        Perform a cleaning cycle on this structure.

        Returns:
            A status string confirming the clean and its effects.
        """

    @property
    @abstractmethod
    def cleanliness(self) -> float:
        """Current cleanliness score (0–100)."""


# ===========================================================================
# Enclosure
# ===========================================================================

class Enclosure(ICleanable):
    """
    A managed space that houses animals in OzZoo.

    Each enclosure has a habitat_type requirement; only animals whose
    habitat_type matches may be placed inside.  Cleanliness degrades
    daily and is restored by calling clean().

    Attributes:
        name          (str):   Display name (e.g. "Koala Korner").
        habitat_type  (str):   Accepted animal habitat type.
        capacity      (int):   Maximum number of animals.
        _animals      (list):  Animals currently housed here.
        _cleanliness  (float): 0 = filthy, 100 = spotless.
        upgrade_level (int):   0 = basic; higher = more capacity / appeal.
    """

    UPGRADE_COSTS: list[float] = [0, 5_000, 12_000, 25_000]  # cost of each level

    def __init__(
        self,
        name: str,
        habitat_type: str,
        capacity: int = 5,
    ) -> None:
        self.name = name
        self.habitat_type = habitat_type
        self._capacity: int = capacity
        self._animals: list[Animal] = []
        self.__cleanliness: float = 100.0   # name-mangled
        self.upgrade_level: int = 0
        self.maintenance_cost_per_day: float = 50.0

    # ------------------------------------------------------------------
    # ICleanable implementation
    # ------------------------------------------------------------------

    @property
    def cleanliness(self) -> float:
        return self.__cleanliness

    def clean(self) -> str:
        """
        Restore cleanliness to 100 % and boost animal happiness.

        Returns:
            A status string describing the clean.
        """
        boost = 100.0 - self.__cleanliness
        self.__cleanliness = 100.0
        for animal in self._animals:
            animal.happiness = min(100.0, animal.happiness + boost * 0.3)
        return (
            f"🧹 '{self.name}' has been cleaned! "
            f"Cleanliness restored to 100% (+happiness for residents)."
        )

    # ------------------------------------------------------------------
    # Animal management
    # ------------------------------------------------------------------

    @property
    def capacity(self) -> int:
        return self._capacity + (self.upgrade_level * 2)

    @property
    def animals(self) -> list[Animal]:
        return list(self._animals)

    def add_animal(self, animal: Animal) -> str:
        """
        Place *animal* into this enclosure after compatibility checks.

        Raises:
            HabitatCapacityExceededError: Enclosure is full.
            InvalidEnclosureTypeError:    Animal requires a different habitat.
            IncompatibleSpeciesError:     Animal conflicts with a resident.
        """
        if len(self._animals) >= self.capacity:
            raise HabitatCapacityExceededError(self.name, self.capacity)

        if animal.habitat_type != self.habitat_type:
            raise InvalidEnclosureTypeError(
                animal.species, animal.habitat_type, self.habitat_type
            )

        # Check for inter-species incompatibility (e.g. Dingo vs Koala).
        for resident in self._animals:
            incompatible = getattr(animal, "incompatible_species", set())
            if resident.species in incompatible:
                raise IncompatibleSpeciesError(
                    animal.species,
                    resident.species,
                    "predator-prey conflict",
                )

        self._animals.append(animal)
        animal.enclosure = self.name
        return f"✅ {animal.name} ({animal.species}) moved into '{self.name}'."

    def remove_animal(self, animal: Animal) -> str:
        """Remove *animal* from this enclosure."""
        if animal in self._animals:
            self._animals.remove(animal)
            animal.enclosure = None
            return f"📦 {animal.name} has been removed from '{self.name}'."
        return f"⚠  {animal.name} is not in '{self.name}'."

    # ------------------------------------------------------------------
    # Daily tick
    # ------------------------------------------------------------------

    def tick(self) -> list[str]:
        """
        Advance enclosure state by one game-day.

        Returns:
            Event strings for the EventBus.
        """
        events: list[str] = []

        # Cleanliness degrades proportional to occupancy.
        dirt_rate = max(2.0, len(self._animals) * 3.0)
        self.__cleanliness = max(0.0, self.__cleanliness - dirt_rate)

        if self.__cleanliness < 20:
            for animal in self._animals:
                animal.happiness -= 5
                animal.health -= 2
            events.append(
                f"🤢 '{self.name}' is filthy (cleanliness {self.__cleanliness:.0f}%)! "
                "Animals are unhappy — clean this enclosure now."
            )
        elif self.__cleanliness < 50:
            events.append(
                f"⚠  '{self.name}' is getting dirty ({self.__cleanliness:.0f}%). "
                "Consider scheduling a clean."
            )

        # Random maintenance event (5 % chance).
        if random.random() < 0.05:
            events.append(
                f"🔧 '{self.name}' needs a maintenance check — "
                "a fence post is looking wobbly."
            )

        return events

    def upgrade(self, treasury: "Treasury") -> str:  # type: ignore[name-defined]  # noqa: F821
        """
        Upgrade the enclosure to the next level, increasing capacity.

        Raises:
            ValueError:             Already at maximum level.
            InsufficientFundsError: Treasury cannot cover cost.
        """
        from systems.patterns import Treasury  # local import avoids circular

        next_level = self.upgrade_level + 1
        if next_level >= len(self.UPGRADE_COSTS):
            return f"'{self.name}' is already at the maximum upgrade level."
        cost = self.UPGRADE_COSTS[next_level]
        treasury.debit(cost, f"Enclosure upgrade: '{self.name}' → Level {next_level}")
        self.upgrade_level = next_level
        self.maintenance_cost_per_day += 25
        return (
            f"🏗  '{self.name}' upgraded to Level {self.upgrade_level}! "
            f"New capacity: {self.capacity} animals."
        )

    def visitor_appeal(self) -> float:
        """
        Calculate how attractive this enclosure is to visitors (0–100).

        Appeal is based on animal health, happiness, and enclosure cleanliness.
        """
        if not self._animals:
            return 0.0
        avg_health = sum(a.health for a in self._animals) / len(self._animals)
        avg_happy = sum(a.happiness for a in self._animals) / len(self._animals)
        return (avg_health * 0.4) + (avg_happy * 0.4) + (self.cleanliness * 0.2)

    def __repr__(self) -> str:
        return (
            f"Enclosure(name={self.name!r}, type={self.habitat_type!r}, "
            f"animals={len(self._animals)}/{self.capacity})"
        )


# ===========================================================================
# Habitat (different from Enclosure — a wider ecological zone)
# ===========================================================================

class Habitat(ICleanable):
    """
    A large ecological zone within OzZoo (e.g. the Australian Bush walk).

    Unlike a single Enclosure, a Habitat can contain multiple enclosures
    and models a broader environmental area.  Implements ICleanable so
    rangers can clean the shared pathways and visitor areas.

    Attributes:
        name         (str):         Display name.
        description  (str):         Visitor-facing blurb.
        enclosures   (list):        All enclosures within this habitat.
        _cleanliness (float):       Shared pathway / amenity cleanliness.
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._enclosures: list[Enclosure] = []
        self.__cleanliness: float = 100.0

    @property
    def cleanliness(self) -> float:
        return self.__cleanliness

    @property
    def enclosures(self) -> list[Enclosure]:
        return list(self._enclosures)

    def add_enclosure(self, enclosure: Enclosure) -> None:
        """Register an enclosure as part of this habitat."""
        self._enclosures.append(enclosure)

    def clean(self) -> str:
        """Clean shared paths and amenities within this habitat."""
        self.__cleanliness = 100.0
        return (
            f"🌿 '{self.name}' habitat pathways and amenities have been cleaned!"
        )

    def tick(self) -> list[str]:
        """Daily degradation of habitat cleanliness."""
        self.__cleanliness = max(0.0, self.__cleanliness - 5.0)
        events: list[str] = []
        if self.__cleanliness < 30:
            events.append(
                f"🍂 '{self.name}' habitat is looking neglected "
                f"(cleanliness {self.__cleanliness:.0f}%) — visitors are unhappy."
            )
        return events

    def total_visitor_appeal(self) -> float:
        """Average appeal across all enclosures in this habitat."""
        if not self._enclosures:
            return 0.0
        return sum(e.visitor_appeal() for e in self._enclosures) / len(self._enclosures)


# ===========================================================================
# Visitor
# ===========================================================================

class Visitor:
    """
    Represents an individual zoo visitor on a given game-day.

    Visitors arrive with a budget and a satisfaction score that changes as
    they move through the zoo.  Satisfied visitors tip and write positive
    reviews; unsatisfied visitors leave bad reviews.

    Attributes:
        name         (str):   Display name.
        budget       (float): Spending budget (AUD) for the day.
        satisfaction (float): Current satisfaction (0–100).
        spent        (float): Amount spent in the zoo so far.
    """

    _visitor_count: int = 0   # class-level counter for unique IDs

    def __init__(self, name: str | None = None, budget: float | None = None) -> None:
        Visitor._visitor_count += 1
        self.name = name or f"Visitor #{Visitor._visitor_count:04d}"
        self.budget: float = budget or random.uniform(25.0, 120.0)
        self.__satisfaction: float = 50.0   # name-mangled
        self.spent: float = 0.0
        self.admission_paid: bool = False

    @property
    def satisfaction(self) -> float:
        return self.__satisfaction

    @satisfaction.setter
    def satisfaction(self, value: float) -> None:
        self.__satisfaction = max(0.0, min(100.0, value))

    def pay_admission(self, ticket_price: float) -> float:
        """
        Pay the entrance fee and return the revenue collected.

        Returns 0 if the visitor cannot afford the ticket.
        """
        if self.budget >= ticket_price:
            self.budget -= ticket_price
            self.spent += ticket_price
            self.admission_paid = True
            self.satisfaction += 5
            return ticket_price
        return 0.0

    def visit_enclosure(self, enclosure: "Enclosure") -> float:
        """
        Visit an enclosure; adjust satisfaction based on appeal.

        Returns:
            Revenue generated (food stall spending etc.).
        """
        appeal = enclosure.visitor_appeal()
        # Scale satisfaction delta: full appeal (+20), zero appeal (-20).
        delta = (appeal - 50) * 0.4
        self.satisfaction += delta

        # Spend at the gift shop when happy.
        revenue = 0.0
        if self.satisfaction > 60 and self.budget > 10:
            spend = min(self.budget, random.uniform(5, 20))
            self.budget -= spend
            self.spent += spend
            revenue = spend
        return revenue

    def leave_review(self) -> str:
        """Generate a review string based on final satisfaction."""
        if self.satisfaction >= 80:
            return f"⭐⭐⭐⭐⭐ {self.name}: 'Absolutely magnificent — I'll be back!'"
        elif self.satisfaction >= 60:
            return f"⭐⭐⭐⭐  {self.name}: 'Great day out, really enjoyed the animals.'"
        elif self.satisfaction >= 40:
            return f"⭐⭐⭐   {self.name}: 'Decent zoo, but some enclosures looked a bit sad.'"
        elif self.satisfaction >= 20:
            return f"⭐⭐    {self.name}: 'Disappointed — animals looked unwell.'"
        else:
            return f"⭐     {self.name}: 'Terrible experience — animal welfare concerns!'"

    def donate(self) -> float:
        """Happy visitors may donate extra funds."""
        if self.satisfaction >= 75 and self.budget >= 10:
            donation = random.uniform(5, 30)
            self.budget -= donation
            self.spent += donation
            return round(donation, 2)
        return 0.0


# ===========================================================================
# Zoo — Singleton
# ===========================================================================

class Zoo:
    """
    The central Singleton that owns all enclosures, animals, and finances.

    There is exactly one Zoo instance per game session.  It exposes the
    high-level management API used by the CLI — buy animals, build
    enclosures, run the daily tick, etc.

    Pattern:
        Singleton (Gamma et al., 1994).  __new__ ensures only one instance
        ever exists; get_instance() is the canonical access point.
    """

    _instance: "Zoo | None" = None

    def __new__(cls, name: str = "OzZoo", *args, **kwargs) -> "Zoo":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self, name: str = "OzZoo", starting_balance: float = 50_000.0) -> None:
        if self._initialised:
            return
        self._initialised = True

        from systems.patterns import Treasury, FoodStore, MedicineStore, EventBus

        self.name: str = name
        self.day: int = 1
        self.ticket_price: float = 25.00
        self._habitats: list[Habitat] = []
        self._all_enclosures: list[Enclosure] = []
        self._all_animals: list[Animal] = []
        self.treasury = Treasury(starting_balance)
        self.food_store = FoodStore.get_instance()
        self.medicine_store = MedicineStore.get_instance()
        self.event_bus = EventBus.get_instance()
        self.reputation: float = 60.0   # 0–100 public reputation score
        self._daily_events: list[str] = []

    @classmethod
    def get_instance(cls, **kwargs) -> "Zoo":
        if cls._instance is None:
            cls(**kwargs)
        return cls._instance

    # ------------------------------------------------------------------
    # Infrastructure management
    # ------------------------------------------------------------------

    def build_enclosure(
        self,
        name: str,
        habitat_type: str,
        capacity: int = 5,
    ) -> Enclosure:
        """
        Construct a new enclosure and charge the treasury.

        Returns:
            The newly constructed Enclosure.
        """
        build_cost = 10_000.0 + capacity * 500.0
        self.treasury.debit(build_cost, f"Build enclosure: '{name}'")
        enc = Enclosure(name, habitat_type, capacity)
        self._all_enclosures.append(enc)
        self._daily_events.append(
            f"🏗  New enclosure '{name}' ({habitat_type}) built for ${build_cost:,.2f}."
        )
        return enc

    def add_habitat(self, habitat: Habitat) -> None:
        """Register a pre-constructed Habitat with the zoo."""
        self._habitats.append(habitat)
        for enc in habitat.enclosures:
            if enc not in self._all_enclosures:
                self._all_enclosures.append(enc)

    # ------------------------------------------------------------------
    # Animal management
    # ------------------------------------------------------------------

    def purchase_animal(self, species: str, name: str, enclosure: Enclosure) -> str:
        """
        Buy an animal from the registry and place it in *enclosure*.

        Raises:
            ValueError:                 Unknown species.
            InsufficientFundsError:     Cannot afford the animal.
            HabitatCapacityExceededError / InvalidEnclosureTypeError / etc.
        """
        from systems.patterns import AnimalFactory

        animal = AnimalFactory.create(species, name)
        price = animal.purchase_price
        self.treasury.debit(price, f"Purchase animal: {name} ({species})")
        result = enclosure.add_animal(animal)
        self._all_animals.append(animal)
        return f"🦘 Purchased {name} ({species}) for ${price:,.2f}.\n{result}"

    def feed_animal(self, animal: Animal, food_type: str, kg: float) -> str:
        """
        Feed *animal* — demonstrates polymorphism.

        The same call works for Koala, Kangaroo, Emu, or any other Animal
        subclass; each subtype's eat() method handles the species-specific
        dietary logic.

        Raises:
            InsufficientFoodError: Not enough food in the store.
        """
        self.food_store.consume(food_type, kg)
        return animal.eat(food_type, kg)

    def treat_animal(self, animal: Animal, medicine: str) -> str:
        """Administer medicine to a sick animal."""
        self.medicine_store.use(medicine)
        return animal.administer_medicine(medicine)

    def attempt_breeding(self, a1: Animal, a2: Animal) -> str:
        """Attempt to breed two animals and register the offspring."""
        offspring = a1.breed(a2)
        if offspring is None:
            return (
                f"💔 Breeding between {a1.name} and {a2.name} was unsuccessful. "
                "Ensure both animals are healthy, happy, and at least one year old."
            )
        # Place offspring in the same enclosure as parent.
        for enc in self._all_enclosures:
            if a1 in enc.animals:
                try:
                    msg = enc.add_animal(offspring)
                    self._all_animals.append(offspring)
                    return (
                        f"🍼 {a1.name} and {a2.name} have produced offspring: "
                        f"{offspring.name}!\n{msg}"
                    )
                except Exception as e:
                    return f"🍼 Offspring {offspring.name} born but enclosure full: {e}"
        return f"🍼 Offspring {offspring.name} born — assign to an enclosure."

    # ------------------------------------------------------------------
    # Daily tick
    # ------------------------------------------------------------------

    def advance_day(self) -> list[str]:
        """
        Simulate one full game-day.

        Returns:
            All events that occurred during the day.
        """
        from systems.patterns import Treasury
        from systems.exceptions import AnimalHealthCriticalError

        self._daily_events = []
        self.treasury.set_day(self.day)
        self._daily_events.append(f"\n{'='*60}")
        self._daily_events.append(f"   🌅 DAY {self.day} — OzZoo Daily Report")
        self._daily_events.append(f"{'='*60}")

        # --- Animal ticks ---
        for animal in list(self._all_animals):
            events = animal.tick()
            self._daily_events.extend(events)

            # Health-critical check → Observer event.
            if animal.health <= animal.CRITICAL_HEALTH:
                self.event_bus.publish(
                    "HEALTH_CRITICAL",
                    {"animal": animal.name, "health": animal.health},
                )
                self._daily_events.append(
                    f"🚨 ALERT: {animal.name} health at {animal.health:.0f}%!"
                )

            # Death check.
            if animal.health <= 0:
                self._all_animals.remove(animal)
                for enc in self._all_enclosures:
                    if animal in enc.animals:
                        enc.remove_animal(animal)
                self._daily_events.append(
                    f"💀 Tragedy: {animal.name} ({animal.species}) has died. "
                    "Visitor satisfaction has dropped."
                )
                self.reputation -= 5

        # --- Enclosure ticks ---
        for enc in self._all_enclosures:
            events = enc.tick()
            self._daily_events.extend(events)
            self.treasury.debit(
                enc.maintenance_cost_per_day,
                f"Maintenance: '{enc.name}'"
            )

        # --- Habitat ticks ---
        for hab in self._habitats:
            self._daily_events.extend(hab.tick())

        # --- Visitors ---
        visitor_count = self._simulate_visitors()
        self._daily_events.append(
            f"🎟  {visitor_count} visitors attended today. "
            f"Treasury: {self.treasury.summary()}"
        )

        # --- Reputation decay ---
        avg_health = (
            sum(a.health for a in self._all_animals) / len(self._all_animals)
            if self._all_animals else 50.0
        )
        rep_delta = (avg_health - 60) * 0.05
        self.reputation = max(0.0, min(100.0, self.reputation + rep_delta))

        # --- Special events (10 % chance) ---
        self._daily_events.extend(self._random_event())

        self.day += 1
        return self._daily_events

    def _simulate_visitors(self) -> int:
        """Run the visitor simulation and collect revenue."""
        base_visitors = int(self.reputation * 0.8)
        visitor_count = max(0, base_visitors + random.randint(-5, 10))
        total_revenue = 0.0

        for _ in range(visitor_count):
            v = Visitor()
            revenue = v.pay_admission(self.ticket_price)
            total_revenue += revenue

            for enc in self._all_enclosures:
                revenue += v.visit_enclosure(enc)
                total_revenue += v.donate()

        if total_revenue > 0:
            self.treasury.credit(total_revenue, f"Day {self.day} visitor revenue")
        return visitor_count

    def _random_event(self) -> list[str]:
        """Generate a random special event (10 % probability)."""
        events = []
        if random.random() < 0.10:
            event = random.choice([
                ("🌡  Heatwave hits OzZoo! All animal happiness −10.", "heatwave"),
                ("🌧  Heavy rain — visitors stay home today.", "rain"),
                ("📰  OzZoo featured in the Herald Sun! Reputation +5.", "media"),
                ("🎉  School excursion arrives — bonus revenue!", "excursion"),
                ("🦠  Quarantine scare — one random animal is sick.", "quarantine"),
            ])
            events.append(event[0])
            if event[1] == "heatwave":
                for a in self._all_animals:
                    a.happiness -= 10
            elif event[1] == "media":
                self.reputation = min(100, self.reputation + 5)
            elif event[1] == "excursion":
                self.treasury.credit(500, "School excursion visit")
            elif event[1] == "quarantine":
                if self._all_animals:
                    sick = random.choice(self._all_animals)
                    sick.is_sick = True
                    sick.health -= 10
                    events.append(f"🤒 {sick.name} has been placed under observation.")
        return events

    # ------------------------------------------------------------------
    # Convenience getters
    # ------------------------------------------------------------------

    @property
    def all_animals(self) -> list[Animal]:
        return list(self._all_animals)

    @property
    def all_enclosures(self) -> list[Enclosure]:
        return list(self._all_enclosures)

    def get_animal_by_name(self, name: str) -> Animal | None:
        """Find an animal by name (case-insensitive)."""
        name_lower = name.lower()
        for a in self._all_animals:
            if a.name.lower() == name_lower:
                return a
        return None

    def get_enclosure_by_name(self, name: str) -> Enclosure | None:
        """Find an enclosure by name (case-insensitive)."""
        name_lower = name.lower()
        for e in self._all_enclosures:
            if e.name.lower() == name_lower:
                return e
        return None

    def __repr__(self) -> str:
        return (
            f"Zoo(name={self.name!r}, day={self.day}, "
            f"animals={len(self._all_animals)}, "
            f"enclosures={len(self._all_enclosures)})"
        )
