"""
animals/base.py — Abstract base classes and full animal taxonomy for OzZoo.

Class hierarchy
---------------
Animal (ABC)                   ← level 0 (abstract)
    Mammal(Animal)             ← level 1 (abstract)
        Marsupial(Mammal)      ← level 2 (abstract)
            Koala(Marsupial)   ← level 3 (concrete)
            Kangaroo(Marsupial)
            Wombat(Marsupial)
        Canid(Mammal)
            Dingo(Canid)
    Bird(Animal)               ← level 1 (abstract)
        FlightlessBird(Bird)   ← level 2 (abstract)
            Emu(FlightlessBird)
        Raptor(Bird)
            WedgeTailEagle(Raptor)
    Reptile(Animal)            ← level 1 (abstract)
        Monitor(Reptile)       ← level 2 (abstract)
            Goanna(Monitor)

OOP patterns demonstrated
--------------------------
* Abstraction   — Animal, Mammal, Bird, Reptile are ABCs; make_sound() and
                  get_dietary_needs() are abstract.
* Inheritance   — three-level depth throughout the taxonomy.
* Polymorphism  — feed(), make_sound(), and breed() behave differently per
                  concrete class without the caller caring about the subtype.
* Encapsulation — health, hunger, and happiness are name-mangled (__health
                  etc.) and exposed only through properties + setters.

Author : Babatundji Williams-Fulwood
Student ID : s8138393
Unit : NIT2112 Object Oriented Programming — Victoria University
"""

from __future__ import annotations

import random
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass  # avoid circular imports at runtime


# ===========================================================================
# Shared data container
# ===========================================================================

@dataclass
class AnimalStats:
    """
    Immutable snapshot of an animal's vital statistics at a given game tick.

    Attributes:
        name       (str):   Display name of the individual animal.
        species    (str):   Scientific / common species label.
        health     (float): Current health percentage (0–100).
        hunger     (float): Hunger level — 0 = full, 100 = starving.
        happiness  (float): Happiness percentage (0–100).
        age        (int):   Age in game-days.
        is_sick    (bool):  True if the animal requires veterinary care.
    """

    name: str
    species: str
    health: float
    hunger: float
    happiness: float
    age: int
    is_sick: bool


# ===========================================================================
# IBreedable interface (ABC with only abstract methods)
# ===========================================================================

class IBreedable(ABC):
    """
    Interface contract for animals that can reproduce inside OzZoo.

    Any class implementing IBreedable must define can_breed() and breed().
    This mirrors the concept of a Java/C# interface achieved through Python's
    ABC mechanism.
    """

    @abstractmethod
    def can_breed(self) -> bool:
        """Return True if this individual meets all breeding pre-conditions."""

    @abstractmethod
    def breed(self, partner: "Animal") -> "Animal | None":
        """
        Attempt to produce offspring with *partner*.

        Returns:
            A new Animal instance if breeding succeeds, otherwise None.
        """


# ===========================================================================
# Abstract base — Animal
# ===========================================================================

class Animal(IBreedable):
    """
    Abstract root of the OzZoo animal taxonomy.

    All concrete animals inherit from Animal (at least two levels deep) and
    must implement the abstract methods declared here.  The class uses
    name-mangled attributes for health, hunger, and happiness to enforce
    encapsulation — external code must use the provided properties.

    Attributes:
        animal_id  (str):   Unique UUID assigned at birth / acquisition.
        name       (str):   Individual name (e.g. "Bindi").
        age        (int):   Age in game-days.
        is_sick    (bool):  Veterinary flag.
        enclosure  (str | None): Name of the current enclosure.
    """

    # Breeding requires health AND happiness above these thresholds.
    BREED_HEALTH_MIN: float = 70.0
    BREED_HAPPINESS_MIN: float = 60.0
    CRITICAL_HEALTH: float = 20.0

    def __init__(self, name: str) -> None:
        self.animal_id: str = str(uuid.uuid4())[:8].upper()
        self.name: str = name
        self.age: int = 0
        self.is_sick: bool = False
        self.enclosure: str | None = None

        # Name-mangled — accessible only via properties below.
        self.__health: float = 100.0
        self.__hunger: float = 0.0       # 0 = full, 100 = starving
        self.__happiness: float = 80.0

    # ------------------------------------------------------------------
    # Properties — enforce valid ranges (encapsulation)
    # ------------------------------------------------------------------

    @property
    def health(self) -> float:
        """Current health percentage (0–100)."""
        return self.__health

    @health.setter
    def health(self, value: float) -> None:
        self.__health = max(0.0, min(100.0, value))

    @property
    def hunger(self) -> float:
        """Hunger level (0 = full, 100 = starving)."""
        return self.__hunger

    @hunger.setter
    def hunger(self, value: float) -> None:
        self.__hunger = max(0.0, min(100.0, value))

    @property
    def happiness(self) -> float:
        """Happiness percentage (0–100)."""
        return self.__happiness

    @happiness.setter
    def happiness(self, value: float) -> None:
        self.__happiness = max(0.0, min(100.0, value))

    # ------------------------------------------------------------------
    # Abstract methods — subclasses MUST override these
    # ------------------------------------------------------------------

    @abstractmethod
    def make_sound(self) -> str:
        """Return the vocalisation string unique to this species."""

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]:
        """
        Return a mapping of food-type → kg required per game-day.

        Example:
            {"Eucalyptus": 1.5}
        """

    @property
    @abstractmethod
    def species(self) -> str:
        """Common species name used in UI and logs."""

    @property
    @abstractmethod
    def habitat_type(self) -> str:
        """Enclosure type this animal requires (e.g. 'Bush', 'Aviary')."""

    @property
    @abstractmethod
    def purchase_price(self) -> float:
        """Base cost to acquire this animal (AUD)."""

    # ------------------------------------------------------------------
    # IBreedable concrete helpers (subclasses may override breed())
    # ------------------------------------------------------------------

    def can_breed(self) -> bool:
        """
        Default breeding eligibility check.

        An animal can breed when healthy, happy, adult (≥365 days old),
        not sick, and not at critical health.
        """
        return (
            self.health >= self.BREED_HEALTH_MIN
            and self.happiness >= self.BREED_HAPPINESS_MIN
            and self.age >= 365
            and not self.is_sick
        )

    def breed(self, partner: "Animal") -> "Animal | None":
        """
        Default breeding — returns a same-species offspring if eligible.

        Args:
            partner (Animal): The potential breeding partner.

        Returns:
            A new Animal of the same concrete type, or None on failure.
        """
        if (
            type(self) is not type(partner)
            or not self.can_breed()
            or not partner.can_breed()
        ):
            return None
        if random.random() < 0.5:    # 50 % success chance
            offspring_name = f"Baby {self.species} #{random.randint(100, 999)}"
            # Instantiate a fresh copy of the concrete subclass.
            return type(self)(offspring_name)
        return None

    # ------------------------------------------------------------------
    # Tick — called every game-day
    # ------------------------------------------------------------------

    def tick(self) -> list[str]:
        """
        Advance the animal's state by one game-day.

        Returns:
            A list of event strings (warnings, status changes) for the
            EventSystem / CLI to process.
        """
        events: list[str] = []
        self.age += 1

        # Hunger increases daily; rate depends on species activity.
        hunger_rate = self._hunger_rate()
        self.hunger += hunger_rate

        # Health deteriorates when hungry.
        if self.hunger > 50:
            health_loss = (self.hunger - 50) * 0.3
            self.health -= health_loss
            events.append(
                f"⚠  {self.name} is hungry ({self.hunger:.0f}%) — health dropping."
            )

        # Happiness falls when health is low.
        if self.health < 50:
            self.happiness -= 5
            events.append(f"😟 {self.name} is unhappy (health {self.health:.0f}%).")

        # Random illness chance (1 % per tick).
        if not self.is_sick and random.random() < 0.01:
            self.is_sick = True
            self.health -= 10
            events.append(f"🤒 {self.name} has fallen ill — veterinary care required!")

        # Sick animals deteriorate faster.
        if self.is_sick:
            self.health -= 5
            self.happiness -= 10
            events.append(f"🏥 {self.name} is sick — health {self.health:.0f}%.")

        return events

    def _hunger_rate(self) -> float:
        """Subclasses may override to model species-specific metabolism."""
        return 8.0   # default: 8 % hunger increase per day

    # ------------------------------------------------------------------
    # Feeding (called by ZooManager.feed_animal — polymorphic target)
    # ------------------------------------------------------------------

    def eat(self, food_type: str, amount_kg: float) -> str:
        """
        Consume food and update hunger / happiness accordingly.

        Args:
            food_type (str):   The variety of food offered.
            amount_kg (float): Kilograms of food offered.

        Returns:
            A status string describing the meal outcome.
        """
        needs = self.get_dietary_needs()
        if food_type not in needs:
            return (
                f"🚫 {self.name} sniffs and turns away — "
                f"{food_type} is not part of their diet."
            )

        required = needs[food_type]
        ratio = min(amount_kg / required, 1.0)
        self.hunger = max(0.0, self.hunger - (ratio * 100))
        self.happiness = min(100.0, self.happiness + (ratio * 10))
        self.health = min(100.0, self.health + (ratio * 5))

        if ratio >= 1.0:
            return f"😋 {self.name} enjoyed a full meal of {amount_kg:.1f} kg {food_type}."
        return (
            f"😐 {self.name} was partially fed ({amount_kg:.1f}/{required:.1f} kg "
            f"{food_type}) — still a bit hungry."
        )

    # ------------------------------------------------------------------
    # Veterinary care
    # ------------------------------------------------------------------

    def administer_medicine(self, medicine_name: str) -> str:
        """
        Treat a sick animal and restore some health.

        Args:
            medicine_name (str): Name of the medicine administered.

        Returns:
            A status string.
        """
        if not self.is_sick:
            return f"ℹ  {self.name} is not currently sick — medicine not needed."
        self.is_sick = False
        self.health = min(100.0, self.health + 30)
        return (
            f"💊 {self.name} has been treated with {medicine_name}. "
            f"Health restored to {self.health:.0f}%."
        )

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def get_stats(self) -> AnimalStats:
        """Return a frozen AnimalStats snapshot for display / logging."""
        return AnimalStats(
            name=self.name,
            species=self.species,
            health=self.health,
            hunger=self.hunger,
            happiness=self.happiness,
            age=self.age,
            is_sick=self.is_sick,
        )

    def __repr__(self) -> str:  # noqa: D105
        return (
            f"{type(self).__name__}(id={self.animal_id!r}, "
            f"name={self.name!r}, health={self.health:.0f}%)"
        )


# ===========================================================================
# Level-1 abstract — Mammal
# ===========================================================================

class Mammal(Animal):
    """
    Abstract intermediate class for all OzZoo mammals.

    Adds mammalian traits (fur_type, social_group_size) and overrides
    _hunger_rate() to reflect warm-blooded metabolism.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.fur_type: str = "Short"
        self.social_group_size: int = 1

    def _hunger_rate(self) -> float:
        return 10.0   # mammals eat more than reptiles

    @property
    @abstractmethod
    def species(self) -> str: ...  # still abstract — concrete subclass fills in

    @property
    @abstractmethod
    def habitat_type(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


# ===========================================================================
# Level-2 abstract — Marsupial
# ===========================================================================

class Marsupial(Mammal):
    """
    Abstract class for all marsupials — Koala, Kangaroo, Wombat.

    Marsupials have a pouch_young attribute tracking the number of joeys
    currently in the pouch, and benefit from specialised eucalyptus diets.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.pouch_young: int = 0
        self.fur_type = "Thick"

    @property
    def habitat_type(self) -> str:
        return "Bush"

    @property
    @abstractmethod
    def species(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


# ===========================================================================
# Level-3 concrete — Marsupials
# ===========================================================================

class Koala(Marsupial):
    """
    Koala — iconic Australian marsupial.

    Koalas are sedentary, sleep up to 20 hours a day, and subsist almost
    entirely on eucalyptus leaves.  Their low energy diet means they have
    a slower hunger rate but are very sensitive to habitat quality.

    References:
        Australian Koala Foundation. (2023). *Koala facts*.
        https://www.savethekoala.com/about-koalas/koala-facts/
    """

    @property
    def species(self) -> str:
        return "Koala"

    @property
    def purchase_price(self) -> float:
        return 8_500.00

    def _hunger_rate(self) -> float:
        return 5.0   # slow metabolism — lots of sleeping

    def make_sound(self) -> str:
        return f"{self.name} lets out a deep, bellowing snore. 😴"

    def get_dietary_needs(self) -> dict[str, float]:
        return {"Eucalyptus": 1.5}

    def tick(self) -> list[str]:
        events = super().tick()
        # Koalas thrive in a clean, cool environment.
        if self.enclosure and self.happiness < 40:
            events.append(
                f"🍃 {self.name} looks stressed — consider cleaning the enclosure."
            )
        return events


class Kangaroo(Marsupial):
    """
    Eastern Grey Kangaroo — the symbol of Australia.

    Kangaroos are highly social (mob animals) and require grassland space
    for hopping.  Their happiness bonus scales with group size.

    References:
        Parks Victoria. (2023). *Eastern grey kangaroo*.
        https://www.parks.vic.gov.au/get-into-nature/wildlife-in-victoria/kangaroos
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.social_group_size = 5

    @property
    def habitat_type(self) -> str:
        return "Savannah"

    @property
    def species(self) -> str:
        return "Eastern Grey Kangaroo"

    @property
    def purchase_price(self) -> float:
        return 3_200.00

    def _hunger_rate(self) -> float:
        return 12.0   # active grazers

    def make_sound(self) -> str:
        return f"{self.name} stamps a powerful foot — THUMP! 🦘"

    def get_dietary_needs(self) -> dict[str, float]:
        return {"Grass": 3.0, "Hay": 1.0}


class Wombat(Marsupial):
    """
    Common Wombat — sturdy, nocturnal burrower.

    Wombats are solitary and territorial but delight visitors with their
    cube-shaped droppings, which have become an OzZoo talking point.

    References:
        Wombat Protection Society of Australia. (2022). *About wombats*.
        https://www.wombatprotectionsociety.org/
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.burrow_depth: int = 0   # cm dug — cosmetic stat

    @property
    def habitat_type(self) -> str:
        return "Savannah"

    @property
    def species(self) -> str:
        return "Common Wombat"

    @property
    def purchase_price(self) -> float:
        return 4_000.00

    def make_sound(self) -> str:
        return f"{self.name} lets out a low, grumpy grunt. 🟫"

    def get_dietary_needs(self) -> dict[str, float]:
        return {"Grass": 2.0, "Roots": 0.5}

    def tick(self) -> list[str]:
        events = super().tick()
        self.burrow_depth += random.randint(1, 5)
        if self.age % 30 == 0:
            events.append(
                f"🕳  {self.name} has dug their burrow to {self.burrow_depth} cm deep!"
            )
        return events


# ===========================================================================
# Level-2 concrete — Canid
# ===========================================================================

class Canid(Mammal):
    """Abstract class for canine species."""

    @property
    def habitat_type(self) -> str:
        return "Savannah"

    @property
    @abstractmethod
    def species(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


class Dingo(Canid):
    """
    Australian Dingo — apex predator of the outback.

    Dingoes are highly intelligent and require mental stimulation (enrichment
    activities) to maintain happiness.  They cannot coexist with sheep or
    small mammals in the same enclosure.

    References:
        Wallach, A. D., Johnson, C. N., Ritchie, E. G., & O'Neill, A. J.
        (2010). Predator control promotes invasive dominated plant communities.
        *Journal of Applied Ecology, 47*(6), 1269–1277.
        https://doi.org/10.1111/j.1365-2664.2010.01871.x
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.pack_size: int = 1
        self.incompatible_species = {"Koala", "Common Wombat"}

    @property
    def species(self) -> str:
        return "Dingo"

    @property
    def purchase_price(self) -> float:
        return 5_500.00

    def make_sound(self) -> str:
        return f"{self.name} raises its head and HOWLS into the night. 🐺"

    def get_dietary_needs(self) -> dict[str, float]:
        return {"Raw Meat": 1.5, "Bone": 0.3}

    def _hunger_rate(self) -> float:
        return 13.0


# ===========================================================================
# Level-1 abstract — Bird
# ===========================================================================

class Bird(Animal):
    """
    Abstract class for all OzZoo birds.

    Birds have a wing_span attribute (cosmetic) and require aviary-type
    enclosures.  Their hunger rate is moderate.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.wing_span_cm: float = 50.0

    def _hunger_rate(self) -> float:
        return 7.0

    @property
    @abstractmethod
    def species(self) -> str: ...

    @property
    @abstractmethod
    def habitat_type(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


# ===========================================================================
# Level-2 abstract — FlightlessBird
# ===========================================================================

class FlightlessBird(Bird):
    """Abstract class for flightless bird species."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.running_speed_kmh: float = 0.0

    @property
    def habitat_type(self) -> str:
        return "Savannah"

    @property
    @abstractmethod
    def species(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


class Emu(FlightlessBird):
    """
    Emu — Australia's tallest native bird.

    Emus are curious and will investigate anything shiny.  They are highly
    entertaining for visitors when energetic and well-fed.

    References:
        Davies, S. J. J. F. (2002). *Ratites and tinamous*. Oxford University
        Press.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.running_speed_kmh = 48.0
        self.wing_span_cm = 25.0   # vestigial wings

    @property
    def species(self) -> str:
        return "Emu"

    @property
    def purchase_price(self) -> float:
        return 2_800.00

    def make_sound(self) -> str:
        return f"{self.name} makes a thunderous BOOMING drum sound. 🥁"

    def get_dietary_needs(self) -> dict[str, float]:
        return {"Seeds": 0.8, "Grass": 1.2, "Insects": 0.2}

    def tick(self) -> list[str]:
        events = super().tick()
        if self.happiness > 70 and random.random() < 0.1:
            events.append(
                f"🏃 {self.name} is sprinting laps — visitors love it!"
            )
        return events


# ===========================================================================
# Level-2 abstract — Raptor
# ===========================================================================

class Raptor(Bird):
    """Abstract class for birds of prey."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.territory_km2: float = 10.0

    @property
    def habitat_type(self) -> str:
        return "Aviary"

    def _hunger_rate(self) -> float:
        return 6.0   # raptors eat large meals infrequently

    @property
    @abstractmethod
    def species(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


class WedgeTailEagle(Raptor):
    """
    Wedge-tailed Eagle — Australia's largest bird of prey.

    With a wingspan of up to 230 cm, the wedge-tail is a flagship species
    for OzZoo.  Their presence significantly boosts visitor satisfaction.

    References:
        Olsen, P. (1995). *Australian birds of prey*. University of New
        South Wales Press.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.wing_span_cm = 230.0

    @property
    def species(self) -> str:
        return "Wedge-tailed Eagle"

    @property
    def purchase_price(self) -> float:
        return 12_000.00

    def make_sound(self) -> str:
        return f"{self.name} lets out a high, piercing KEEEE! 🦅"

    def get_dietary_needs(self) -> dict[str, float]:
        return {"Raw Meat": 0.8}

    def tick(self) -> list[str]:
        events = super().tick()
        if self.happiness > 70:
            events.append(
                f"🦅 {self.name} soars majestically — visitor happiness +5!"
            )
        return events


# ===========================================================================
# Level-1 abstract — Reptile
# ===========================================================================

class Reptile(Animal):
    """
    Abstract class for all OzZoo reptiles.

    Reptiles are ectothermic (cold-blooded), so their enclosures must
    maintain specific temperatures.  They have a slower metabolism than
    mammals.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.is_ectotherm: bool = True
        self.preferred_temp_c: float = 28.0

    def _hunger_rate(self) -> float:
        return 4.0   # slow metabolism

    @property
    @abstractmethod
    def species(self) -> str: ...

    @property
    @abstractmethod
    def habitat_type(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


# ===========================================================================
# Level-2 abstract — Monitor
# ===========================================================================

class Monitor(Reptile):
    """Abstract class for monitor lizards (goannas and relatives)."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.tongue_flicks: int = 0   # cosmetic sensory counter

    @property
    def habitat_type(self) -> str:
        return "Reptile House"

    @property
    @abstractmethod
    def species(self) -> str: ...

    @property
    @abstractmethod
    def purchase_price(self) -> float: ...

    @abstractmethod
    def make_sound(self) -> str: ...

    @abstractmethod
    def get_dietary_needs(self) -> dict[str, float]: ...


class Goanna(Monitor):
    """
    Lace Monitor (Goanna) — Australia's second-largest lizard.

    Goannas are opportunistic predators that fascinate visitors but can be
    intimidating.  Their presence in the Reptile House is a highlight.

    References:
        Shine, R. (1986). Food habits, habitats and reproductive biology of
        four sympatric species of varanid lizards in tropical Australia.
        *Herpetologica, 42*(3), 346–360.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.preferred_temp_c = 32.0

    @property
    def species(self) -> str:
        return "Lace Monitor (Goanna)"

    @property
    def purchase_price(self) -> float:
        return 3_500.00

    def make_sound(self) -> str:
        self.tongue_flicks += 1
        return f"{self.name} flicks its tongue rapidly and hisses. 🦎"

    def get_dietary_needs(self) -> dict[str, float]:
        return {"Raw Meat": 0.6, "Eggs": 0.2}

    def tick(self) -> list[str]:
        events = super().tick()
        self.tongue_flicks += 1
        return events
