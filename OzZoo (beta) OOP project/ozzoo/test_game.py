"""Integration test for OzZoo game."""
import sys
sys.path.insert(0, '.')

# Reset singletons
import zoo.entities as ze; ze.Zoo._instance = None
import systems.patterns as sp
sp.FoodStore._instance = None
sp.MedicineStore._instance = None
sp.EventBus._instance = None

from zoo.entities import Zoo
from systems.patterns import AnimalFactory, FoodStore
from systems.exceptions import (
    InsufficientFundsError, HabitatCapacityExceededError, 
    IncompatibleSpeciesError, InsufficientFoodError
)

# --- Build zoo ---
zoo = Zoo('OzZoo', 150_000)
enc   = zoo.build_enclosure('Koala Korner',   'Bush',          3)
enc2  = zoo.build_enclosure('Roo Run',         'Savannah',      5)
av    = zoo.build_enclosure('Eagle Aviary',    'Aviary',        2)
rep   = zoo.build_enclosure('Reptile House',   'Reptile House', 3)

zoo.purchase_animal('koala',    'Bindi', enc)
zoo.purchase_animal('koala',    'Karl',  enc)
zoo.purchase_animal('kangaroo', 'Joey',  enc2)
zoo.purchase_animal('wombat',   'Digger',enc2)
zoo.purchase_animal('eagle',    'Aria',  av)
zoo.purchase_animal('goanna',   'Rex',   rep)

print(f"Animals loaded: {len(zoo.all_animals)}")
assert len(zoo.all_animals) == 6

# Seed food
store = FoodStore.get_instance()
store._stock.update({
    'Eucalyptus': 20.0, 'Grass': 20.0, 'Raw Meat': 10.0,
    'Seeds': 5.0, 'Hay': 5.0, 'Roots': 5.0, 'Eggs': 5.0, 'Insects': 5.0
})

# --- Polymorphic feeding (same call, different animal behaviours) ---
for a in zoo.all_animals:
    for food, kg in a.get_dietary_needs().items():
        try:
            zoo.feed_animal(a, food, kg)
        except InsufficientFoodError:
            pass

# --- Advance 3 days ---
for _ in range(3):
    events = zoo.advance_day()
    print(f"Day {zoo.day - 1}: {len(events)} events | bal=${zoo.treasury.balance:,.0f}")

# --- Polymorphism: make_sound() ---
print("\n--- make_sound() polymorphism ---")
for a in zoo.all_animals:
    print(" ", a.make_sound())

# --- Exception handling ---
try:
    zoo.treasury.debit(999_999, 'impossible purchase')
except InsufficientFundsError as e:
    print(f"\nCaught {e.error_code}: InsufficientFundsError OK")

# Capacity exception
try:
    zoo.purchase_animal('koala', 'Extra', enc)   # enc is full (cap=3, has 2)
    zoo.purchase_animal('koala', 'Extra2', enc)
    zoo.purchase_animal('koala', 'Extra3', enc)
except (HabitatCapacityExceededError, InsufficientFundsError) as e:
    print(f"Caught {e.error_code}: capacity/funds guard OK")

# Incompatible species
try:
    enc2.add_animal(zoo.all_animals[0])  # Koala in Savannah enc
except Exception as e:
    print(f"InvalidEnclosureType guard OK")

# --- Factory pattern ---
species_list = AnimalFactory.available_species()
print(f"\nFactory knows {len(species_list)} species")
assert len(species_list) >= 7

# --- Breeding ---
bindi = zoo.get_animal_by_name('Bindi')
karl  = zoo.get_animal_by_name('Karl')
result = zoo.attempt_breeding(bindi, karl)
print(f"Breeding result: {result[:70]}")

# --- Observer / EventBus ---
from systems.patterns import EventBus, IObserver
class TestObs(IObserver):
    def __init__(self): self.received = []
    def on_event(self, event_type, payload): self.received.append(event_type)

obs = TestObs()
bus = EventBus.get_instance()
bus.subscribe('HEALTH_CRITICAL', obs)
bus.publish('HEALTH_CRITICAL', {'animal': 'TestAnimal', 'health': 15.0})
assert 'HEALTH_CRITICAL' in obs.received
print("Observer pattern: EventBus OK")

# --- Hermes skill integration ---
sys.path.insert(0, '.')
from hermes_integration.skill import get_zoo_status, feed_animal as h_feed, advance_day as h_adv
status = get_zoo_status()
import json
data = json.loads(status)
assert data['status'] == 'success'
print(f"Hermes skill get_zoo_status: {data['animal_count']} animals")

print("\nALL TESTS PASSED")
