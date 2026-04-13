"""
hermes_integration/skill.py — OzZoo skill for the Hermes Agent framework.

This module exposes OzZoo game-logic as callable Python functions that
the Hermes Agent (Nous Research) can execute as part of its skill system.
When integrated, you can interact with OzZoo through natural language
via the Hermes CLI.

Setup
-----
1.  Install Hermes Agent:
        git clone https://github.com/NousResearch/hermes-agent.git
        cd hermes-agent && pip install -e ".[all,dev]"

2.  Copy (or symlink) this file into your Hermes skills directory:
        mkdir -p ~/.hermes/skills/ozzoo
        cp hermes_integration/skill.py ~/.hermes/skills/ozzoo/skill.py

3.  Launch Hermes with the skill enabled:
        hermes chat --toolsets skills

4.  Example prompts to Hermes:
        "Show me the current status of OzZoo."
        "Feed Kiki with 2 kg of Eucalyptus."
        "What animals are sick in OzZoo today?"
        "Advance the zoo by one day and report what happened."

Reference:
    Nous Research. (2024). *Hermes-Agent: An open-source AI agent
    framework*. GitHub. https://github.com/NousResearch/hermes-agent

Author : Babatundji Williams-Fulwood
Student ID : s8138393
Unit : NIT2112 Object Oriented Programming — Victoria University
"""

from __future__ import annotations

import json
import sys
import os

# Allow importing OzZoo modules when running from the hermes skills dir.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from zoo.entities import Zoo, Enclosure
from systems.patterns import AnimalFactory, FoodStore, MedicineStore
from systems.exceptions import OzZooBaseException


# ===========================================================================
# Module-level zoo singleton (persists for the Hermes session)
# ===========================================================================

def _get_zoo() -> Zoo:
    """Return (or initialise) the global OzZoo singleton."""
    zoo = Zoo.get_instance()
    # Seed the zoo if empty (first call in this Hermes session).
    if not zoo.all_enclosures:
        _seed_zoo(zoo)
    return zoo


def _seed_zoo(zoo: Zoo) -> None:
    """Quickly populate the zoo for the Hermes demo session."""
    try:
        bush = zoo.build_enclosure("Koala Korner", "Bush", 3)
        sav = zoo.build_enclosure("Roo Run", "Savannah", 6)
        zoo.purchase_animal("Koala", "Kiki", bush)
        zoo.purchase_animal("Kangaroo", "Joey", sav)
        zoo.purchase_animal("Kangaroo", "Sheila", sav)
        # Seed food
        FoodStore.get_instance()._stock.update({
            "Eucalyptus": 20.0, "Grass": 30.0,
        })
    except OzZooBaseException:
        pass


# ===========================================================================
# Hermes-callable skill functions
# ===========================================================================

def get_zoo_status() -> str:
    """
    Return the current status of OzZoo as a JSON string.

    Returns:
        JSON with keys: day, balance, reputation, animal_count,
        enclosure_count, and a list of animal summaries.

    Example Hermes prompt:
        "What is the current state of my zoo?"
    """
    zoo = _get_zoo()
    animals_data = []
    for a in zoo.all_animals:
        animals_data.append({
            "name": a.name,
            "species": a.species,
            "health": round(a.health, 1),
            "hunger": round(a.hunger, 1),
            "happiness": round(a.happiness, 1),
            "is_sick": a.is_sick,
            "enclosure": a.enclosure,
        })
    return json.dumps({
        "status": "success",
        "day": zoo.day,
        "balance": round(zoo.treasury.balance, 2),
        "reputation": round(zoo.reputation, 1),
        "animal_count": len(zoo.all_animals),
        "enclosure_count": len(zoo.all_enclosures),
        "animals": animals_data,
    }, indent=2)


def feed_animal(animal_name: str, food_type: str, amount_kg: float) -> str:
    """
    Feed a named animal with a specified food type and quantity.

    Args:
        animal_name (str):   The individual animal's name (e.g. "Kiki").
        food_type   (str):   The food variety (e.g. "Eucalyptus").
        amount_kg   (float): Kilograms of food to provide.

    Returns:
        JSON status string describing the feeding outcome.

    Example Hermes prompt:
        "Feed Kiki with 1.5 kg of Eucalyptus."
    """
    zoo = _get_zoo()
    animal = zoo.get_animal_by_name(animal_name)
    if animal is None:
        return json.dumps({"status": "error", "message": f"Animal '{animal_name}' not found."})
    try:
        result = zoo.feed_animal(animal, food_type, amount_kg)
        return json.dumps({"status": "success", "message": result})
    except OzZooBaseException as e:
        return json.dumps({"status": "error", "message": str(e)})


def advance_day() -> str:
    """
    Advance OzZoo by one game-day and return all events that occurred.

    Returns:
        JSON with a list of event strings and the new day number.

    Example Hermes prompt:
        "Advance the zoo by one day and tell me what happened."
    """
    zoo = _get_zoo()
    events = zoo.advance_day()
    return json.dumps({
        "status": "success",
        "new_day": zoo.day,
        "events": events,
    }, indent=2)


def get_sick_animals() -> str:
    """
    Return a list of all animals currently requiring veterinary attention.

    Returns:
        JSON list of sick animal summaries.

    Example Hermes prompt:
        "Which animals are sick and need treatment?"
    """
    zoo = _get_zoo()
    sick = [
        {"name": a.name, "species": a.species, "health": round(a.health, 1)}
        for a in zoo.all_animals if a.is_sick
    ]
    return json.dumps({
        "status": "success",
        "sick_count": len(sick),
        "sick_animals": sick,
    })


def treat_animal(animal_name: str, medicine: str) -> str:
    """
    Administer medicine to a sick animal.

    Args:
        animal_name (str): Name of the animal to treat.
        medicine    (str): Medicine name from the vet cabinet.

    Returns:
        JSON status string.

    Example Hermes prompt:
        "Treat Kiki with General Antibiotic."
    """
    zoo = _get_zoo()
    animal = zoo.get_animal_by_name(animal_name)
    if animal is None:
        return json.dumps({"status": "error", "message": f"'{animal_name}' not found."})
    try:
        result = zoo.treat_animal(animal, medicine)
        return json.dumps({"status": "success", "message": result})
    except OzZooBaseException as e:
        return json.dumps({"status": "error", "message": str(e)})


def buy_food(food_type: str, kg: float) -> str:
    """
    Purchase food stock for the zoo.

    Args:
        food_type (str):   Food variety to buy.
        kg        (float): Kilograms to purchase.

    Returns:
        JSON status string with new stock level.

    Example Hermes prompt:
        "Purchase 10 kg of Eucalyptus."
    """
    zoo = _get_zoo()
    store = FoodStore.get_instance()
    try:
        result = store.purchase(food_type, kg, zoo.treasury)
        return json.dumps({"status": "success", "message": result})
    except (OzZooBaseException, ValueError) as e:
        return json.dumps({"status": "error", "message": str(e)})


def list_available_species() -> str:
    """
    Return a list of all purchasable animal species and their prices.

    Returns:
        JSON list of species with prices.

    Example Hermes prompt:
        "What animals can I buy for my zoo?"
    """
    species_data = []
    for sp in AnimalFactory.available_species():
        try:
            price = AnimalFactory.get_price(sp)
            species_data.append({"species": sp, "price_aud": price})
        except ValueError:
            pass
    return json.dumps({"status": "success", "available_species": species_data})


def get_food_stock() -> str:
    """
    Return the current food inventory levels.

    Returns:
        JSON mapping food type → kilograms in stock.

    Example Hermes prompt:
        "How much food do we have left?"
    """
    stock = FoodStore.get_instance().stock()
    return json.dumps({"status": "success", "food_stock_kg": stock})


def make_animal_sound(animal_name: str) -> str:
    """
    Trigger an animal's make_sound() method (demonstrates polymorphism).

    Args:
        animal_name (str): The individual animal's name.

    Returns:
        JSON with the sound string.

    Example Hermes prompt:
        "What sound does Kiki make?"
    """
    zoo = _get_zoo()
    animal = zoo.get_animal_by_name(animal_name)
    if animal is None:
        return json.dumps({"status": "error", "message": f"'{animal_name}' not found."})
    sound = animal.make_sound()
    return json.dumps({"status": "success", "sound": sound})
