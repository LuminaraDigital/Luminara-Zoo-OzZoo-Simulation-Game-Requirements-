"""Luminara Zoo orchestrator: Singleton façade with day loop, resources, observers."""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from animals.animal import Animal
from animals.factory import AnimalFactory, AnimalFactoryError
from animals.interfaces import IBreedable
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
    InvalidAmountError,
    InvalidCapacityError,
)
from systems.food_store import FoodStore
from systems.medicine_store import MedicineStore
from systems.special_events import SpecialEvents
from systems.treasury import Treasury
from zoo.enclosure import Enclosure
from zoo.habitat import Habitat
from zoo.visitor import VisitorDay


class Zoo:
    """Singleton façade coordinating animals, habitats, economy, and time."""

    __singleton_lock = threading.Lock()
    __instance: Optional["Zoo"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Zoo":
        if cls.__instance is None:
            with cls.__singleton_lock:
                if cls.__instance is None:
                    cls.__instance = super().__new__(cls)
                    cls.__instance.__dict__["_Zoo__initialised"] = False
        return cls.__instance

    def __init__(self, capacity: int = 24) -> None:
        if self.__initialised:
            return
        try:
            if not isinstance(capacity, int) or capacity <= 0:
                raise InvalidCapacityError(
                    "Zoo capacity must be a positive integer.",
                    capacity=capacity if isinstance(capacity, int) else None,
                )
            self.__capacity = capacity
            self.__animals: List[Animal] = []
            self.__treasury = Treasury()
            self.__day = 1
            self.__ticket_price_aud = 28.0
            self.__event_bus = EventBus()
            self.__event_bus.subscribe(AlertObserver())
            koala_enc = Enclosure("Koala Korner", 4, {"Marsupial"})
            roo_enc = Enclosure("Roo Run", 6, {"Marsupial"})
            dingo_enc = Enclosure("Dingo Ridge", 3, {"Canid"})
            bird_enc = Enclosure("Eagle's Roost", 4, {"Bird"})
            rept_enc = Enclosure("Reptile House", 3, {"Reptile"})
            self.__enclosures = [koala_enc, roo_enc, dingo_enc, bird_enc, rept_enc]
            self.__habitats: List[Habitat] = [
                Habitat("Bushlands", [koala_enc, roo_enc]),
                Habitat("Predator Ridge", [dingo_enc]),
                Habitat("Sky Aviary Complex", [bird_enc]),
                Habitat("Reptile Row", [rept_enc]),
            ]
            self.__placement: Dict[str, str] = {}
            self.__last_visitor_summary: Dict[str, Any] = {}
            self.__reputation_streak = 0
            self.__award_ledger = AwardLedger()
            self.__pending_award_titles: List[str] = []
        except InvalidCapacityError:
            raise
        except Exception as exc:  # pragma: no cover
            raise InvalidCapacityError(
                "Failed to initialise zoo capacity state.",
                capacity=capacity if isinstance(capacity, int) else None,
                cause=exc,
            ) from exc
        self.__dict__["_Zoo__initialised"] = True

    @classmethod
    def reset_for_testing(cls) -> None:
        with cls.__singleton_lock:
            cls.__instance = None
        FoodStore.reset_for_testing()
        MedicineStore.reset_for_testing()

    @property
    def __initialised(self) -> bool:
        return bool(self.__dict__.get("_Zoo__initialised", False))

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def population(self) -> int:
        return len(self.__animals)

    @property
    def treasury(self) -> Treasury:
        return self.__treasury

    @property
    def current_day(self) -> int:
        return self.__day

    @property
    def ticket_price_aud(self) -> float:
        return self.__ticket_price_aud

    @ticket_price_aud.setter
    def ticket_price_aud(self, value: float) -> None:
        v = float(value)
        if v <= 0:
            raise InvalidAmountError("Ticket price must be positive.", amount=v)
        self.__ticket_price_aud = round(v, 2)

    @property
    def reputation_score(self) -> int:
        """Park reputation (0–100) from average welfare — drives the win streak."""
        alive = [a for a in self.__animals if a.is_alive]
        if not alive:
            return 40
        total = sum((a.health + a.happiness + a.cleanliness) / 3.0 for a in alive)
        return max(0, min(100, int(round(total / len(alive)))))

    @property
    def reputation_streak_days(self) -> int:
        """Consecutive days with reputation ≥80 and positive treasury (Tutorial win metric)."""
        return self.__reputation_streak

    @property
    def has_won_campaign(self) -> bool:
        """True once the manager holds elite reputation long enough."""
        return self.__reputation_streak >= 30

    def _enqueue_awards(self, titles: List[str]) -> None:
        """Collect trophy titles for the CLI to announce (additive feature)."""
        self.__pending_award_titles.extend(titles)

    def drain_award_announcements(self) -> List[str]:
        """Pop queued award titles for one-shot UI messages."""
        out = list(self.__pending_award_titles)
        self.__pending_award_titles.clear()
        return out

    def list_animals(self) -> List[Animal]:
        return list(self.__animals)

    def enclosures(self) -> List[Enclosure]:
        return list(self.__enclosures)

    def habitats(self) -> List[Habitat]:
        """Ecological zones (Tutorial ``Habitat``) grouping physical enclosures."""
        return list(self.__habitats)

    def find_enclosure(self, label: str) -> Optional[Enclosure]:
        key = label.strip().lower()
        for enc in self.__enclosures:
            if enc.label.lower() == key:
                return enc
        return None

    def habitat_of(self, animal: Animal) -> Optional[str]:
        return self.__placement.get(animal.name)

    def add_animal(self, animal: Animal) -> None:
        try:
            if len(self.__animals) >= self.__capacity:
                raise CapacityExceededError(
                    "Cannot admit another animal: zoo at capacity.",
                    limit=self.__capacity,
                    attempted_total=len(self.__animals) + 1,
                )
            self.__animals.append(animal)
        except CapacityExceededError:
            raise
        except Exception as exc:  # pragma: no cover
            raise CapacityExceededError(
                "Unexpected failure while admitting an animal.",
                limit=self.__capacity,
                attempted_total=len(self.__animals),
                cause=exc,
            ) from exc

    def auto_assign_habitat(self, animal: Animal) -> str:
        """Place ``animal`` in the first compatible enclosure with space."""
        for enc in self.__enclosures:
            try:
                enc.try_assign(animal)
                self.__placement[animal.name] = enc.label
                return enc.label
            except (IncompatibleSpeciesError, CapacityExceededError):
                continue
        raise IncompatibleSpeciesError(
            f"No vacant compatible habitat for {animal.name} ({animal.family}). "
            "Expand enclosures or move residents.",
            family=animal.family,
        )

    def assign_to_enclosure(self, animal: Animal, enclosure_label: str) -> str:
        """Move ``animal`` into a named enclosure."""
        enc = self.find_enclosure(enclosure_label)
        if enc is None:
            raise IncompatibleSpeciesError(f"No habitat named '{enclosure_label}'.")
        old_label = self.__placement.get(animal.name)
        if old_label:
            old = self.find_enclosure(old_label)
            if old:
                old.release(animal.name)
        enc.try_assign(animal)
        self.__placement[animal.name] = enc.label
        return f"{animal.name} → {enc.label}"

    def adopt_species(self, species_key: str, name: str) -> Animal:
        """Purchase and admit a new animal via the ``AnimalFactory``."""
        price = AnimalFactory.adoption_price(species_key)
        self.__treasury.debit(price, context="animal_adoption")
        try:
            animal = AnimalFactory.create(species_key, name=name)
        except AnimalFactoryError:
            try:
                self.__treasury.credit(price, context="adoption_rollback")
            except InvalidAmountError:
                pass
            raise
        try:
            self.add_animal(animal)
            self.auto_assign_habitat(animal)
        except Exception:
            if animal in self.__animals:
                self.__animals.remove(animal)
            try:
                self.__treasury.credit(price, context="adoption_rollback")
            except InvalidAmountError:
                pass
            raise
        self._enqueue_awards(self.__award_ledger.on_adopt_success(self))
        return animal

    def get_animal_by_name(self, name: str) -> Animal:
        key = name.strip().lower()
        for a in self.__animals:
            if a.name.lower() == key:
                return a
        raise AnimalNotFoundError(f"No resident named {name!r}.")

    def feed_animal(self, animal: Animal, food_offered: str, meal_cost: float = 12.5) -> str:
        if animal not in self.__animals:
            raise AnimalNotFoundError(
                f"{getattr(animal, 'name', 'Unknown')} is not a registered resident."
            )
        try:
            self.__treasury.debit(meal_cost, context="feed_animal")
        except (InsufficientFundsError, InvalidAmountError):
            raise
        except Exception as exc:  # pragma: no cover
            raise InsufficientFundsError(
                "Unexpected treasury failure during feeding.",
                required=meal_cost,
                available=self.__treasury.balance,
                cause=exc,
            ) from exc
        try:
            msg = animal.eat(food_offered)
            self._enqueue_awards(self.__award_ledger.on_feed_success(self))
            return msg
        except FeedingError:
            try:
                self.__treasury.credit(meal_cost, context="feed_animal_rollback")
            except InvalidAmountError:
                pass
            raise
        except Exception as exc:  # pragma: no cover
            try:
                self.__treasury.credit(meal_cost, context="feed_animal_rollback")
            except InvalidAmountError:
                pass
            raise FeedingError("Feeding failed due to an unexpected error.") from exc

    def feed_from_pantry(self, animal: Animal, food_id: str, prep_fee: float = 6.5) -> str:
        """Consume stocked food then polymorphically feed (pantry + prep labour)."""
        if animal not in self.__animals:
            raise AnimalNotFoundError(f"{animal.name} is not a registered resident.")
        store = FoodStore()
        try:
            store.consume(food_id, 1)
            self.__treasury.debit(prep_fee, context="meal_prep")
        except (InsufficientFoodError, InsufficientFundsError, InvalidAmountError):
            raise
        try:
            msg = animal.eat(food_id)
            self._enqueue_awards(self.__award_ledger.on_feed_success(self))
            return msg
        except FeedingError:
            try:
                self.__treasury.credit(prep_fee, context="meal_prep_rollback")
            except InvalidAmountError:
                pass
            store.restock(food_id, 1)
            raise

    def apply_medicine(self, animal: Animal, medicine_key: str) -> str:
        if animal not in self.__animals:
            raise AnimalNotFoundError(f"{animal.name} is not a registered resident.")
        ms = MedicineStore()
        key = medicine_key.lower().strip()
        if key not in ms.cabinet():
            raise AnimalNotFoundError(f"No medicine {medicine_key!r} in cabinet.")
        med = ms.consume_dose(key)
        try:
            self.__treasury.debit(med.cost_aud, context="medicine_admin")
            out = animal.apply_medicine(health_boost=med.health_boost, mood_boost=med.mood_boost)
            self._enqueue_awards(self.__award_ledger.on_medicine_success(self))
            return out
        except (InsufficientFundsError, InvalidAmountError):
            ms.return_dose(key, 1)
            raise

    def purchase_medicine_doses(self, medicine_key: str, doses: int) -> str:
        """Restock the singleton ``MedicineStore`` (Tutorial menu: Buy Medicine)."""
        msg = MedicineStore().purchase_doses(medicine_key, doses, self.__treasury)
        self._enqueue_awards(self.__award_ledger.on_medicine_restock(self))
        return msg

    def try_breed(
        self,
        parent_a_name: str,
        parent_b_name: str,
        enclosure_label: str,
        offspring_name: str,
        *,
        stud_fee: float = 175.0,
    ) -> Animal:
        """Breed two compatible residents of the same species in a habitat."""
        a = self.get_animal_by_name(parent_a_name)
        b = self.get_animal_by_name(parent_b_name)
        if type(a) is not type(b):
            raise BreedingFailedError("Parents must be the same species.")
        if not isinstance(a, IBreedable):
            raise BreedingFailedError("This species does not support breeding here.")
        enc = self.find_enclosure(enclosure_label)
        if enc is None:
            raise BreedingFailedError(f"Unknown habitat '{enclosure_label}'.")
        if not (enc.contains(a.name) and enc.contains(b.name)):
            raise BreedingFailedError("Both parents must already occupy the chosen habitat.")
        if enc.max_occupants - enc.occupancy() < 1:
            raise BreedingFailedError("Habitat has no spare capacity for offspring.")
        if not (a.can_breed() and b.can_breed()):
            raise BreedingFailedError("One or both parents are not healthy/happy enough to breed.")
        type_to_key = {v: k for k, v in AnimalFactory.supported_species().items()}
        key = type_to_key.get(type(a))
        if key is None:
            raise BreedingFailedError("Factory cannot derive species key.")
        self.__treasury.debit(stud_fee, context="breeding")
        baby = AnimalFactory.create(key, name=offspring_name)
        try:
            self.add_animal(baby)
            self.assign_to_enclosure(baby, enc.label)
        except Exception as exc:
            if baby in self.__animals:
                self.__animals.remove(baby)
            for hab in self.__enclosures:
                hab.release(baby.name)
            self.__placement.pop(baby.name, None)
            try:
                self.__treasury.credit(stud_fee, context="breeding_rollback")
            except InvalidAmountError:
                pass
            raise BreedingFailedError("Breeding failed while placing offspring.") from exc
        self._enqueue_awards(self.__award_ledger.on_breed_success(self))
        return baby

    def purchase_food(self, food_id: str, quantity: int) -> str:
        """Buy pantry stock (delegates to ``FoodStore`` singleton)."""
        msg = FoodStore().purchase(food_id, quantity, self.__treasury)
        self._enqueue_awards(self.__award_ledger.on_food_purchase(self))
        return msg

    def clean_enclosure(self, label: str) -> str:
        enc = self.find_enclosure(label)
        if enc is None:
            raise HabitatNotFoundError(f"No habitat named '{label}'.")
        fee = 45.0
        self.__treasury.debit(fee, context="habitat_cleaning")
        msg = enc.clean()
        self._enqueue_awards(self.__award_ledger.on_clean_success(self))
        return msg

    def advance_day(self) -> Dict[str, Any]:
        """Run one simulation tick: welfare, alerts, visitors, removals."""
        self.__day += 1
        log_lines: List[str] = []

        heatwave = SpecialEvents.roll_heatwave()
        if heatwave:
            self.__event_bus.publish("heatwave", {"day": self.__day})
            log_lines.append("Heatwave event stressed outdoor exhibits.")

        for creature in list(self.__animals):
            if creature.is_alive:
                creature.apply_daily_stress(heatwave=heatwave)
                if creature.health < 20:
                    self.__event_bus.publish(
                        "critical_health",
                        {
                            "day": self.__day,
                            "animal": creature.name,
                            "health": creature.health,
                        },
                    )

        if SpecialEvents.roll_celebration():
            self.__event_bus.publish("celebration", {"day": self.__day})
            for creature in self.__animals:
                if creature.is_alive:
                    creature.happiness = min(100, creature.happiness + 6)
            try:
                self.__treasury.credit(520.0, context="celebration_donations")
            except InvalidAmountError:
                pass
            log_lines.append("Community celebration boosted moods and donations.")

        self.__last_visitor_summary = VisitorDay.simulate(
            self.__animals,
            ticket_price_aud=self.__ticket_price_aud,
            day=self.__day,
            treasury=self.__treasury,
        )
        log_lines.append(str(self.__last_visitor_summary.get("message", "")))

        dead = [x for x in self.__animals if not x.is_alive]
        had_death_today = len(dead) > 0
        for body in dead:
            self.__event_bus.publish(
                "animal_death", {"day": self.__day, "animal": body.name}
            )
            for hab in self.__enclosures:
                hab.release(body.name)
            self.__placement.pop(body.name, None)
        self.__animals = [x for x in self.__animals if x.is_alive]

        if had_death_today:
            self.__reputation_streak = 0
        rep = self.reputation_score
        if not had_death_today:
            if rep >= 80 and self.__treasury.balance > 0:
                self.__reputation_streak += 1
            else:
                self.__reputation_streak = 0
        won = self.has_won_campaign
        if won:
            log_lines.append(
                "★ Luminara milestone: 30 consecutive days of reputation ≥80 with a healthy treasury!"
            )

        day_awards = self.__award_ledger.on_day_end(
            self, had_death_today=had_death_today, heatwave=heatwave
        )
        self._enqueue_awards(day_awards)

        return {
            "day": self.__day,
            "heatwave": heatwave,
            "visitor_summary": self.__last_visitor_summary,
            "log": log_lines,
            "population": self.population,
            "reputation": rep,
            "reputation_streak": self.__reputation_streak,
            "campaign_won": won,
        }

    def get_zoo_status(self) -> dict[str, Any]:
        return {
            "park_name": "Luminara Zoo",
            "day": self.__day,
            "population": self.population,
            "capacity": self.__capacity,
            "funds_aud": self.__treasury.balance,
            "ticket_price_aud": self.__ticket_price_aud,
            "reputation": self.reputation_score,
            "reputation_streak_days": self.reputation_streak_days,
            "campaign_won": self.has_won_campaign,
            "last_visitors": self.__last_visitor_summary,
            "pantry": FoodStore().snapshot_inventory(),
            "medicine_stock": MedicineStore().snapshot_stock(),
            "habitats": [h.describe() for h in self.__habitats],
            "enclosures": [e.describe() for e in self.__enclosures],
            "awards": self.__award_ledger.snapshot(),
            "animals": [
                {
                    "name": a.name,
                    "taxon": a.__class__.__name__,
                    "family": a.family,
                    "habitat": self.__placement.get(a.name),
                    "health": a.health,
                    "hunger": a.hunger,
                    "cleanliness": a.cleanliness,
                    "happiness": a.happiness,
                    "alive": a.is_alive,
                }
                for a in self.__animals
            ],
        }
