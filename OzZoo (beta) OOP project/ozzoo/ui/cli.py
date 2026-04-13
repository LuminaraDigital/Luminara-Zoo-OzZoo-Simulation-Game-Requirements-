"""
ui/cli.py — Command-Line Interface and game loop for OzZoo.

Provides a Rich-powered terminal dashboard and an interactive menu
system.  The game loop is driven by the manager's choices each day.

Author : Babatundji Williams-Fulwood
Student ID : s8138393
Unit : NIT2112 Object Oriented Programming — Victoria University
"""

from __future__ import annotations

import sys
import time
from typing import Callable

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich import box
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from zoo.entities import Zoo, Enclosure, Habitat
from animals.base import Animal
from systems.patterns import (
    AnimalFactory,
    FoodStore,
    MedicineStore,
    EventBus,
    IObserver,
)
from systems.exceptions import OzZooBaseException


console = Console() if RICH_AVAILABLE else None


def cprint(msg: str, style: str = "") -> None:
    """Print with Rich formatting, falling back to plain print."""
    if console:
        console.print(msg, style=style)
    else:
        print(msg)


# ===========================================================================
# Observer — CLI Alert Panel
# ===========================================================================

class AlertObserver(IObserver):
    """
    Concrete Observer that prints urgent alerts to the terminal.

    Registered with the EventBus for HEALTH_CRITICAL events.  When an
    animal's health drops below the threshold the EventBus calls on_event()
    and this observer immediately displays a highlighted warning.
    """

    def on_event(self, event_type: str, payload: dict) -> None:
        if event_type == "HEALTH_CRITICAL":
            animal_name = payload.get("animal", "Unknown")
            health = payload.get("health", 0)
            cprint(
                f"\n🚨 [bold red]HEALTH ALERT[/bold red] — "
                f"[yellow]{animal_name}[/yellow] is at "
                f"[bold red]{health:.0f}%[/bold red] health! "
                "Open the Vet menu immediately.",
                "bold red",
            )


# ===========================================================================
# Helper display functions
# ===========================================================================

def display_banner() -> None:
    """Print the OzZoo welcome banner."""
    banner = r"""
   ___  ___  __          
  / _ \/_  / /_____  ___ 
 / // / / /_/ __/ _ \/ _ \
/____/ /___/\__/\___/\___/
  OzZoo — Your Australian Wildlife Park
    """
    cprint(f"[bold green]{banner}[/bold green]")


def display_zoo_status(zoo: Zoo) -> None:
    """Render the main zoo dashboard panel."""
    if not RICH_AVAILABLE:
        print(f"\n=== OzZoo Status — Day {zoo.day} ===")
        print(f"Balance: ${zoo.treasury.balance:,.2f}")
        print(f"Animals: {len(zoo.all_animals)}")
        print(f"Reputation: {zoo.reputation:.0f}%")
        return

    # Financial panel
    fin_text = Text()
    fin_text.append(f"💰 Balance:    ${zoo.treasury.balance:,.2f}\n", style="green")
    fin_text.append(f"🎟  Ticket:     ${zoo.ticket_price:.2f}\n")
    fin_text.append(f"⭐ Reputation: {zoo.reputation:.0f}/100\n")
    fin_text.append(f"📅 Day:        {zoo.day}")
    fin_panel = Panel(fin_text, title="[bold cyan]Finances[/bold cyan]", border_style="cyan")

    # Animals panel
    animal_lines = Text()
    for a in zoo.all_animals[:8]:
        status = "🤒" if a.is_sick else ("🚨" if a.health < 20 else "✅")
        animal_lines.append(
            f"{status} {a.name:<18} HP:{a.health:>5.0f}%  "
            f"Hunger:{a.hunger:>4.0f}%  😊:{a.happiness:>4.0f}%\n"
        )
    if len(zoo.all_animals) > 8:
        animal_lines.append(f"  ... and {len(zoo.all_animals)-8} more\n", style="dim")
    animal_panel = Panel(
        animal_lines or Text("No animals yet.", style="dim"),
        title=f"[bold yellow]Animals ({len(zoo.all_animals)})[/bold yellow]",
        border_style="yellow",
    )

    # Enclosure panel
    enc_lines = Text()
    for e in zoo.all_enclosures[:6]:
        appeal = e.visitor_appeal()
        enc_lines.append(
            f"🏠 {e.name:<20} [{len(e.animals)}/{e.capacity}]  "
            f"Clean:{e.cleanliness:>4.0f}%  Appeal:{appeal:>4.0f}%\n"
        )
    enc_panel = Panel(
        enc_lines or Text("No enclosures built.", style="dim"),
        title=f"[bold magenta]Enclosures ({len(zoo.all_enclosures)})[/bold magenta]",
        border_style="magenta",
    )

    console.print(Panel(
        Columns([fin_panel, animal_panel, enc_panel]),
        title=f"[bold white]🦘 {zoo.name} — Day {zoo.day}[/bold white]",
        border_style="white",
        box=box.DOUBLE_EDGE,
    ))


def display_animals(zoo: Zoo) -> None:
    """Display a detailed animal table."""
    if not zoo.all_animals:
        cprint("No animals in the zoo yet.", "dim")
        return

    if RICH_AVAILABLE:
        table = Table(title="All Animals", box=box.SIMPLE_HEAD)
        table.add_column("Name", style="cyan")
        table.add_column("Species")
        table.add_column("Age (days)")
        table.add_column("Health", justify="right")
        table.add_column("Hunger", justify="right")
        table.add_column("Happy", justify="right")
        table.add_column("Sick?", justify="center")
        table.add_column("Enclosure")

        for a in zoo.all_animals:
            hp_style = "red" if a.health < 30 else ("yellow" if a.health < 60 else "green")
            table.add_row(
                a.name,
                a.species,
                str(a.age),
                f"[{hp_style}]{a.health:.0f}%[/{hp_style}]",
                f"{a.hunger:.0f}%",
                f"{a.happiness:.0f}%",
                "🤒 YES" if a.is_sick else "✅ No",
                a.enclosure or "—",
            )
        console.print(table)
    else:
        for a in zoo.all_animals:
            stats = a.get_stats()
            print(
                f"{stats.name} ({stats.species}) | "
                f"HP:{stats.health:.0f}% | "
                f"Hunger:{stats.hunger:.0f}% | "
                f"Happy:{stats.happiness:.0f}% | "
                f"Sick:{'Yes' if stats.is_sick else 'No'} | "
                f"Enc:{a.enclosure or '—'}"
            )


# ===========================================================================
# Menu actions
# ===========================================================================

def menu_feed_animals(zoo: Zoo) -> None:
    """Interactive feeding sub-menu."""
    if not zoo.all_animals:
        cprint("No animals to feed!", "yellow")
        return

    display_animals(zoo)
    animal_name = input("\nEnter animal name to feed (or 'back'): ").strip()
    if animal_name.lower() == "back":
        return

    animal = zoo.get_animal_by_name(animal_name)
    if not animal:
        cprint(f"Animal '{animal_name}' not found.", "red")
        return

    needs = animal.get_dietary_needs()
    cprint(f"\n{animal.name} needs: {', '.join(f'{v:.1f}kg {k}' for k, v in needs.items())}")

    food_type = input("Food type: ").strip()
    try:
        kg = float(input("Amount (kg): ").strip())
    except ValueError:
        cprint("Invalid amount.", "red")
        return

    try:
        result = zoo.feed_animal(animal, food_type, kg)
        cprint(result, "green")
    except OzZooBaseException as e:
        cprint(str(e), "red")


def menu_buy_food(zoo: Zoo) -> None:
    """Purchase food supplies."""
    store = FoodStore.get_instance()
    stock = store.stock()

    if RICH_AVAILABLE:
        table = Table(title="Food Store", box=box.SIMPLE_HEAD)
        table.add_column("Food Type")
        table.add_column("Price/kg", justify="right")
        table.add_column("In Stock", justify="right")
        for ft, price in FoodStore.FOOD_PRICES.items():
            table.add_row(ft, f"${price:.2f}", f"{stock.get(ft, 0):.1f} kg")
        console.print(table)
    else:
        for ft, price in FoodStore.FOOD_PRICES.items():
            print(f"{ft}: ${price:.2f}/kg | Stock: {stock.get(ft, 0):.1f} kg")

    food_type = input("\nFood to purchase (or 'back'): ").strip()
    if food_type.lower() == "back":
        return
    try:
        kg = float(input("Kilograms: ").strip())
        result = store.purchase(food_type, kg, zoo.treasury)
        cprint(result, "green")
    except (OzZooBaseException, ValueError) as e:
        cprint(str(e), "red")


def menu_buy_animal(zoo: Zoo) -> None:
    """Purchase a new animal from the registry."""
    species_list = AnimalFactory.available_species()
    cprint("\n[bold]Available species:[/bold]")
    for i, sp in enumerate(species_list, 1):
        try:
            price = AnimalFactory.get_price(sp)
            cprint(f"  {i}. {sp} — ${price:,.2f}")
        except ValueError:
            pass

    species = input("\nSpecies name (or 'back'): ").strip()
    if species.lower() == "back":
        return

    name = input("Give this animal a name: ").strip()
    if not name:
        cprint("Name cannot be empty.", "red")
        return

    if not zoo.all_enclosures:
        cprint("No enclosures built yet! Use 'Build Enclosure' first.", "yellow")
        return

    cprint("\nEnclosures:")
    for i, enc in enumerate(zoo.all_enclosures, 1):
        cprint(f"  {i}. {enc.name} ({enc.habitat_type}) [{len(enc.animals)}/{enc.capacity}]")

    enc_name = input("Enclosure name (or 'back'): ").strip()
    if enc_name.lower() == "back":
        return

    enc = zoo.get_enclosure_by_name(enc_name)
    if not enc:
        cprint(f"Enclosure '{enc_name}' not found.", "red")
        return

    try:
        result = zoo.purchase_animal(species, name, enc)
        cprint(result, "green")
    except OzZooBaseException as e:
        cprint(str(e), "red")
    except ValueError as e:
        cprint(str(e), "red")


def menu_build_enclosure(zoo: Zoo) -> None:
    """Build a new enclosure."""
    habitat_types = ["Bush", "Savannah", "Aviary", "Reptile House"]
    cprint("\nHabitat types: " + ", ".join(habitat_types))
    cprint("Cost formula: $10,000 + $500 per animal capacity slot")

    name = input("Enclosure name: ").strip()
    if not name:
        cprint("Name cannot be empty.", "red")
        return

    h_type = input("Habitat type: ").strip()
    try:
        capacity = int(input("Capacity (animals): ").strip())
    except ValueError:
        cprint("Invalid capacity.", "red")
        return

    try:
        enc = zoo.build_enclosure(name, h_type, capacity)
        cprint(f"✅ Built: {enc}", "green")
    except OzZooBaseException as e:
        cprint(str(e), "red")


def menu_vet_clinic(zoo: Zoo) -> None:
    """Treat sick animals."""
    sick = [a for a in zoo.all_animals if a.is_sick]
    if not sick:
        cprint("No animals currently require veterinary care. 🐾", "green")
        return

    cprint(f"\n[bold red]{len(sick)} animal(s) need treatment:[/bold red]")
    for a in sick:
        cprint(f"  • {a.name} ({a.species}) — HP: {a.health:.0f}%")

    store = MedicineStore.get_instance()
    doses = store.doses()
    cprint("\nMedicine Cabinet:")
    for med, qty in doses.items():
        cprint(f"  {med}: {qty} doses")

    animal_name = input("\nAnimal to treat (or 'back'): ").strip()
    if animal_name.lower() == "back":
        return

    animal = zoo.get_animal_by_name(animal_name)
    if not animal:
        cprint(f"Animal '{animal_name}' not found.", "red")
        return

    medicine = input("Medicine to use: ").strip()
    try:
        result = zoo.treat_animal(animal, medicine)
        cprint(result, "green")
    except OzZooBaseException as e:
        cprint(str(e), "red")


def menu_buy_medicine(zoo: Zoo) -> None:
    """Purchase medicine for the vet cabinet."""
    store = MedicineStore.get_instance()
    cprint("\nMedicine Prices:")
    for med, price in MedicineStore.MEDICINE_PRICES.items():
        doses = store.doses().get(med, 0)
        cprint(f"  {med}: ${price:.2f}/dose — {doses} in stock")

    medicine = input("\nMedicine to buy (or 'back'): ").strip()
    if medicine.lower() == "back":
        return
    try:
        qty = int(input("Quantity: ").strip())
        result = store.purchase(medicine, qty, zoo.treasury)
        cprint(result, "green")
    except (OzZooBaseException, ValueError) as e:
        cprint(str(e), "red")


def menu_clean(zoo: Zoo) -> None:
    """Clean an enclosure."""
    if not zoo.all_enclosures:
        cprint("No enclosures to clean.", "yellow")
        return
    cprint("\nEnclosures:")
    for enc in zoo.all_enclosures:
        cprint(f"  {enc.name} — Cleanliness: {enc.cleanliness:.0f}%")

    enc_name = input("Enclosure to clean (or 'back'): ").strip()
    if enc_name.lower() == "back":
        return
    enc = zoo.get_enclosure_by_name(enc_name)
    if enc:
        # Cleaning costs $100 in labour.
        try:
            zoo.treasury.debit(100, f"Cleaning: '{enc.name}'")
            cprint(enc.clean(), "green")
        except OzZooBaseException as e:
            cprint(str(e), "red")
    else:
        cprint("Enclosure not found.", "red")


def menu_breeding(zoo: Zoo) -> None:
    """Attempt to breed two compatible animals."""
    if len(zoo.all_animals) < 2:
        cprint("Need at least 2 animals for breeding.", "yellow")
        return

    display_animals(zoo)
    name1 = input("\nFirst animal name: ").strip()
    name2 = input("Second animal name: ").strip()

    a1 = zoo.get_animal_by_name(name1)
    a2 = zoo.get_animal_by_name(name2)

    if not a1 or not a2:
        cprint("One or both animals not found.", "red")
        return

    result = zoo.attempt_breeding(a1, a2)
    cprint(result, "cyan")


def menu_set_ticket_price(zoo: Zoo) -> None:
    """Adjust the zoo entrance ticket price."""
    cprint(f"\nCurrent ticket price: ${zoo.ticket_price:.2f}")
    cprint("(Higher prices earn more per visitor but may reduce attendance.)")
    try:
        new_price = float(input("New price (AUD): $").strip())
        if new_price < 0:
            cprint("Price cannot be negative.", "red")
            return
        zoo.ticket_price = new_price
        cprint(f"✅ Ticket price updated to ${zoo.ticket_price:.2f}.", "green")
    except ValueError:
        cprint("Invalid price.", "red")


def menu_upgrade_enclosure(zoo: Zoo) -> None:
    """Upgrade an enclosure to increase capacity."""
    if not zoo.all_enclosures:
        cprint("No enclosures to upgrade.", "yellow")
        return
    for enc in zoo.all_enclosures:
        cprint(
            f"  {enc.name} — Level {enc.upgrade_level} "
            f"(capacity: {enc.capacity})"
        )
    enc_name = input("Enclosure to upgrade (or 'back'): ").strip()
    if enc_name.lower() == "back":
        return
    enc = zoo.get_enclosure_by_name(enc_name)
    if not enc:
        cprint("Not found.", "red")
        return
    try:
        result = enc.upgrade(zoo.treasury)
        cprint(result, "green")
    except OzZooBaseException as e:
        cprint(str(e), "red")


def menu_animal_sounds(zoo: Zoo) -> None:
    """Hear from the animals — demonstrates polymorphism."""
    if not zoo.all_animals:
        cprint("No animals in the zoo.", "dim")
        return
    cprint("\n🔊 The animals of OzZoo speak:")
    for animal in zoo.all_animals:
        cprint(f"  {animal.make_sound()}")


def menu_ledger(zoo: Zoo) -> None:
    """View the financial ledger."""
    ledger = zoo.treasury.get_ledger()[-15:]   # last 15 entries
    if RICH_AVAILABLE:
        table = Table(title="Recent Transactions (last 15)", box=box.SIMPLE_HEAD)
        table.add_column("Day", justify="right")
        table.add_column("Description")
        table.add_column("Amount", justify="right")
        for t in ledger:
            style = "green" if t.amount > 0 else "red"
            table.add_row(str(t.day), t.description, f"[{style}]${abs(t.amount):,.2f}[/{style}]")
        console.print(table)
    else:
        for t in ledger:
            sign = "+" if t.amount > 0 else "-"
            print(f"Day {t.day}: {t.description} | {sign}${abs(t.amount):,.2f}")


# ===========================================================================
# Main game loop
# ===========================================================================

MENU: list[tuple[str, str, Callable]] = [
    ("1", "Advance Day",          lambda z: _advance_day(z)),
    ("2", "View Animals",         display_animals),
    ("3", "Feed Animals",         menu_feed_animals),
    ("4", "Buy Food",             menu_buy_food),
    ("5", "Buy Animal",           menu_buy_animal),
    ("6", "Build Enclosure",      menu_build_enclosure),
    ("7", "Upgrade Enclosure",    menu_upgrade_enclosure),
    ("8", "Clean Enclosure",      menu_clean),
    ("9", "Vet Clinic",           menu_vet_clinic),
    ("10", "Buy Medicine",        menu_buy_medicine),
    ("11", "Breeding Program",    menu_breeding),
    ("12", "Set Ticket Price",    menu_set_ticket_price),
    ("13", "Hear Animal Sounds",  menu_animal_sounds),
    ("14", "Financial Ledger",    menu_ledger),
    ("Q", "Quit Game",            None),
]


def _advance_day(zoo: Zoo) -> None:
    """Run one day and print all events."""
    events = zoo.advance_day()
    for event in events:
        cprint(event)


def print_menu() -> None:
    """Render the action menu."""
    if RICH_AVAILABLE:
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Key", style="bold cyan", width=4)
        table.add_column("Action")
        for key, label, _ in MENU:
            table.add_row(f"[{key}]", label)
        console.print(table)
    else:
        for key, label, _ in MENU:
            print(f"  [{key}] {label}")


def setup_starter_zoo(zoo: Zoo) -> None:
    """
    Configure a starter zoo so the game is immediately playable.

    Creates two enclosures, populates them with animals, and seeds
    the food store — so the player can explore mechanics right away.
    """
    try:
        bush_enc = zoo.build_enclosure("Koala Korner", "Bush", 3)
        sav_enc = zoo.build_enclosure("Roo Run", "Savannah", 6)
        aviary = zoo.build_enclosure("Eagle's Roost", "Aviary", 2)
        reptile = zoo.build_enclosure("Reptile House", "Reptile House", 4)

        zoo.purchase_animal("Koala", "Kiki", bush_enc)
        zoo.purchase_animal("Koala", "Karl", bush_enc)
        zoo.purchase_animal("Kangaroo", "Joey", sav_enc)
        zoo.purchase_animal("Kangaroo", "Sheila", sav_enc)
        zoo.purchase_animal("Wombat", "Digger", sav_enc)
        zoo.purchase_animal("Eagle", "Aria", aviary)
        zoo.purchase_animal("Goanna", "Rex", reptile)

        store = FoodStore.get_instance()
        store._stock.update({
            "Eucalyptus": 30.0, "Grass": 40.0, "Hay": 20.0,
            "Seeds": 10.0, "Raw Meat": 15.0,
        })
    except OzZooBaseException as e:
        cprint(f"[yellow]Setup warning: {e}[/yellow]")


def run_game() -> None:
    """Entry point — initialise everything and start the game loop."""
    display_banner()
    cprint("[bold green]Welcome to OzZoo — Australian Wildlife Park Simulator[/bold green]\n")
    cprint("You are Babatundji, the new manager of OzZoo.")
    cprint("Balance the books, care for the animals, and delight your visitors!\n")

    zoo = Zoo("OzZoo", starting_balance=75_000.0)

    # Register the CLI alert observer.
    alert_obs = AlertObserver()
    zoo.event_bus.subscribe("HEALTH_CRITICAL", alert_obs)

    # Pre-populate with starter animals.
    setup_starter_zoo(zoo)

    cprint("\n[bold cyan]Starter zoo ready![/bold cyan] Seven animals across four enclosures.")
    cprint("Type the number or letter next to an action and press Enter.\n")

    while True:
        display_zoo_status(zoo)
        print_menu()

        choice = input("\nYour choice: ").strip().upper()

        if choice == "Q":
            cprint("\n👋 Thanks for playing OzZoo! G'bye, Manager. 🦘", "bold green")
            break

        # Find matching menu action.
        action_fn = None
        for key, label, fn in MENU:
            if key == choice:
                action_fn = fn
                break

        if action_fn is None:
            cprint(f"Invalid choice '{choice}'. Try again.", "yellow")
        else:
            try:
                action_fn(zoo)
            except OzZooBaseException as e:
                cprint(f"\n⛔ Error: {e}", "bold red")
            except KeyboardInterrupt:
                cprint("\nOperation cancelled.", "yellow")
            except Exception as e:
                cprint(f"\n⛔ Unexpected error: {e}", "bold red")

        input("\n[Press Enter to continue]")
