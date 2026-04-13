"""Text-based interface and central game loop (Luminara Zoo — NIT2112).

Handles all manager I/O, dispatches to ``Zoo`` domain operations, surfaces
``OzZooBaseException`` subclasses as user-facing messages, and supports optional
Rich formatting when installed. Input is read line-by-line; EOF is handled so
non-interactive runners do not crash (defaults + clean exit at main menu).
"""

from __future__ import annotations

import textwrap
from typing import Callable

from systems.exceptions import OzZooBaseException
from zoo.scenario import apply_luminara_starter_scenario
from zoo.zoo import Zoo


def _print_wrapped(msg: str) -> None:
    for line in msg.splitlines():
        print(textwrap.fill(line, width=100))


def _g_int(read: Callable[[str], str], prompt: str, default: int | None = None) -> int:
    raw = (
        read(f"{prompt} [{default}]: ").strip()
        if default is not None
        else read(f"{prompt}: ").strip()
    )
    if not raw and default is not None:
        return default
    return int(raw)


def _g_float(read: Callable[[str], str], prompt: str, default: float | None = None) -> float:
    raw = (
        read(f"{prompt} [{default}]: ").strip()
        if default is not None
        else read(f"{prompt}: ").strip()
    )
    if not raw and default is not None:
        return float(default)
    return float(raw)


def _show_status(zoo: Zoo) -> None:
    st = zoo.get_zoo_status()
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        console.print(
            f"\n[bold cyan]{st.get('park_name', 'Luminara Zoo')}[/] — "
            f"Day {st['day']} | Funds [green]${st['funds_aud']:.2f}[/] | "
            f"Ticket ${st['ticket_price_aud']:.2f} | "
            f"Reputation {st['reputation']}% (streak {st['reputation_streak_days']}/30)"
        )
        if st.get("campaign_won"):
            console.print("[bold yellow]Campaign win achieved — outstanding stewardship![/]")
        t = Table(title="Animals")
        t.add_column("Name")
        t.add_column("Species")
        t.add_column("Habitat")
        t.add_column("H")
        t.add_column("G")
        t.add_column("C")
        t.add_column("M")
        for a in st["animals"]:
            t.add_row(
                a["name"],
                a["taxon"],
                str(a.get("habitat") or "—"),
                str(a["health"]),
                str(a["hunger"]),
                str(a["cleanliness"]),
                str(a["happiness"]),
            )
        console.print(t)
        console.print("[dim]H=health G=hunger C=cleanliness M=mood[/]")
        console.print("[bold]Habitat zones (Tutorial façade):[/]")
        for hz in st.get("habitats", []):
            console.print(f"  • {hz}")
        console.print("[bold]Vet cabinet (doses remaining):[/]")
        for mk, qty in sorted(st.get("medicine_stock", {}).items()):
            console.print(f"  • {mk}: {qty}")
        aw = st.get("awards", {})
        n_aw = len(aw.get("unlocked_ids", []))
        console.print(f"[bold]Awards unlocked:[/] {n_aw} (menu 17 for trophy case)")
    except ImportError:
        print(f"\n{st.get('park_name', 'Luminara Zoo')} — Day {st['day']}")
        print(
            f"Funds ${st['funds_aud']:.2f} | Ticket ${st['ticket_price_aud']:.2f} | "
            f"Reputation {st['reputation']}% | Elite streak {st['reputation_streak_days']}/30 days"
        )
        if st.get("campaign_won"):
            print("★ Campaign win: 30-day elite reputation achieved!")
        print(f"Population {st['population']}/{st['capacity']}")
        print("Habitats:")
        for row in st["enclosures"]:
            print(f"  • {row}")
        print("Pantry (non-zero):")
        pantry = st.get("pantry", {})
        for k in sorted(pantry.keys()):
            if pantry[k]:
                print(f"  • {k}: {pantry[k]}")
        print("Animals:")
        for a in st["animals"]:
            print(
                f"  • {a['name']} ({a['taxon']}) habitat={a.get('habitat')} "
                f"H{a['health']} G{a['hunger']} C{a['cleanliness']} M{a['happiness']}"
            )
        print("Habitat zones:")
        for hz in st.get("habitats", []):
            print(f"  • {hz}")
        print("Vet cabinet (doses):")
        for mk, qty in sorted(st.get("medicine_stock", {}).items()):
            print(f"  • {mk}: {qty}")
        aw = st.get("awards", {})
        print(f"Awards unlocked: {len(aw.get('unlocked_ids', []))} (menu 17)")


def _financial_ledger(zoo: Zoo) -> None:
    print("\n--- Last 15 treasury movements (oldest → newest) ---")
    for row in zoo.treasury.ledger_entries():
        print(
            f"  {row.get('kind','?'):8} ${float(row.get('amount', 0)):.2f} "
            f"[{row.get('context','')}] → balance ${float(row.get('balance_after', 0)):.2f}"
        )


def _flush_award_banners(zoo: Zoo) -> None:
    for title in zoo.drain_award_announcements():
        print(f"\n★ Award unlocked: {title}")


def _awards_hall(zoo: Zoo) -> None:
    snap = zoo.get_zoo_status().get("awards", {})
    trophies = snap.get("trophies", [])
    print("\n--- Luminara Trophy Case ---")
    if not trophies:
        print("  (No awards yet — play without AI; awards unlock from your actions.)")
        return
    for t in trophies:
        print(f"  ★ {t['title']}")
        print(f"    {t['description']}")


def _ai_advisor_menu(zoo: Zoo, read: Callable[[str], str]) -> None:
    """Explicit confirmation + provider pick; simulation never auto-calls this."""
    try:
        from systems.ai_advisor import advisor_status_line, ask_advisor
    except ImportError as exc:  # pragma: no cover
        print(f"AI advisor module unavailable: {exc}")
        return

    print("\n--- Optional AI Park Advisor (external API) ---")
    print(advisor_status_line(zoo))
    print("The game runs fully without this. You must type YES in capitals to spend a credit.")
    gate = read("Type YES to send one advisor request (anything else cancels): ").strip()
    if gate != "YES":
        print("Cancelled — no API call.")
        return
    prov = read("Provider: 1 = OpenAI, 2 = Gemini: ").strip()
    if prov == "1":
        provider = "openai"
    elif prov == "2":
        provider = "gemini"
    else:
        print("Invalid choice — cancelled.")
        return
    question = read("Your question for the advisor: ").strip()
    if not question:
        print("Empty question — cancelled.")
        return
    ok, payload = ask_advisor(provider=provider, user_question=question, zoo=zoo)
    if ok:
        print("\n--- Advisor reply ---")
        _print_wrapped(payload)
    else:
        print(f"\n{payload}")


def run_game_loop(
    *,
    zoo_factory: Callable[[], Zoo] | None = None,
    input_fn: Callable[[str], str] | None = None,
) -> None:
    """Run the Luminara Zoo manager CLI until the player quits."""
    # Windows may report stdin as a TTY even when it is NUL/piped; track real EOF from input().
    eof_on_last_read: list[bool] = [False]

    def _stdin_line(prompt: str) -> str:
        eof_on_last_read[0] = False
        try:
            return input(prompt)
        except EOFError:
            eof_on_last_read[0] = True
            return ""

    read: Callable[[str], str] = input_fn or _stdin_line

    print("=" * 72)
    print("  Luminara Zoo — Australian wildlife stewardship simulation")
    print("  NIT2112 OOP Assessment | Victoria University")
    print("=" * 72)

    try:
        cap = _g_int(read, "Maximum animal capacity", 24)
    except (ValueError, EOFError):
        cap = 24
        print("Invalid capacity — defaulting to 24.")

    try:
        from systems.exceptions import InvalidCapacityError

        Zoo.reset_for_testing()
        zoo = (zoo_factory or Zoo)(capacity=cap)
    except InvalidCapacityError as exc:
        print(f"Cannot start zoo: {exc}")
        return

    _print_wrapped(
        "Win condition (tutorial-aligned): reach 30 consecutive days with reputation >=80% "
        "and a positive treasury. Deaths reset your elite streak."
    )
    ans = read("Load the Luminara starter scenario ($75k + seven named residents)? [y/N]: ").strip().lower()
    if ans == "y" and zoo.population == 0:
        try:
            print(apply_luminara_starter_scenario(zoo))
        except OzZooBaseException as exc:
            print(f"Starter failed: {exc}")

    while True:
        print("\n--- Main Menu ---")
        try:
            from systems.ai_advisor import advisor_status_line

            print(f"[{advisor_status_line(zoo)}]")
        except ImportError:
            pass
        print("1) View zoo status")
        print("2) End day (tick simulation)")
        print("3) Set ticket price")
        print("4) Buy food for pantry")
        print("5) Feed animal (catered meal — debits treasury)")
        print("6) Feed animal from pantry (+ prep fee)")
        print("7) Adopt new animal (Factory)")
        print("8) Move animal to habitat")
        print("9) Clean habitat")
        print("10) Apply medicine")
        print("11) Breed pair (same species, same habitat)")
        print("12) Animal sounds (polymorphism demo)")
        print("13) Financial ledger (last 15 transactions)")
        print("14) Load starter scenario (only if zoo is empty)")
        print("15) Restock vet cabinet (MedicineStore doses)")
        print("16) AI park advisor (optional — manual confirm; OpenAI or Gemini)")
        print("17) Trophy case (view awards)")
        print("0) Quit")
        choice = read("Choose: ").strip()
        if not choice and input_fn is None and eof_on_last_read[0]:
            print(
                "\nEnd of input (no more stdin). "
                "To play interactively, open the Terminal in Cursor/VS Code and run:  python main.py"
            )
            break

        try:
            if choice == "1":
                _show_status(zoo)
            elif choice == "2":
                summary = zoo.advance_day()
                print(f"\n--- Morning report — day {summary['day']} ---")
                for line in summary.get("log", []):
                    print(line)
                vs = summary.get("visitor_summary", {})
                print(vs.get("message", ""))
                print(
                    f"Reputation {summary.get('reputation', 0)}% | "
                    f"Elite streak {summary.get('reputation_streak', 0)}/30"
                )
                if summary.get("campaign_won"):
                    print("★ Campaign win — you sustained elite reputation for 30 days!")
            elif choice == "3":
                p = _g_float(read, "Ticket price (AUD)", zoo.ticket_price_aud)
                zoo.ticket_price_aud = p
                print(f"Ticket price set to ${p:.2f}")
            elif choice == "4":
                _buy_food_menu(zoo, read)
            elif choice == "5":
                _feed_catered(zoo, read)
            elif choice == "6":
                _feed_pantry(zoo, read)
            elif choice == "7":
                _adopt_menu(zoo, read)
            elif choice == "8":
                _move_habitat(zoo, read)
            elif choice == "9":
                lab = read("Habitat label (e.g. Koala Korner, Roo Run): ").strip()
                msg = zoo.clean_enclosure(lab)
                print(msg)
            elif choice == "10":
                _medicine_menu(zoo, read)
            elif choice == "11":
                _breed_menu(zoo, read)
            elif choice == "12":
                _sounds_demo(zoo)
            elif choice == "13":
                _financial_ledger(zoo)
            elif choice == "14":
                if zoo.population > 0:
                    print("Starter is only available when the zoo has no animals (reset game).")
                else:
                    print(apply_luminara_starter_scenario(zoo))
            elif choice == "15":
                _restock_medicine_menu(zoo, read)
            elif choice == "16":
                _ai_advisor_menu(zoo, read)
            elif choice == "17":
                _awards_hall(zoo)
            elif choice == "0":
                print("Thanks for stewarding Luminara Zoo!")
                break
            else:
                print("Unknown option.")
        except OzZooBaseException as exc:
            print(f"\n[!] {exc.__class__.__name__}: {exc}")
        except (ValueError, EOFError) as exc:
            print(f"\n[!] Input error: {exc}")
        except KeyboardInterrupt:
            print("\nInterrupted — exiting.")
            break
        else:
            _flush_award_banners(zoo)


def _buy_food_menu(zoo: Zoo, read: Callable[[str], str]) -> None:
    from systems.food_store import FoodStore

    catalog = FoodStore().list_catalog()
    print("Catalog (food_id — price):")
    for item in catalog:
        print(f"  {item.food_id:14} ${item.unit_price_aud:.2f}  {item.display_name}")
    fid = read("food_id: ").strip()
    qty = _g_int(read, "Quantity", 5)
    msg = zoo.purchase_food(fid, qty)
    print(msg)


def _feed_catered(zoo: Zoo, read: Callable[[str], str]) -> None:
    name = read("Animal name: ").strip()
    food = read("Food token (e.g. grass): ").strip()
    cost = _g_float(read, "Meal service cost (AUD)", 12.5)
    animal = zoo.get_animal_by_name(name)
    print(zoo.feed_animal(animal, food, cost))


def _feed_pantry(zoo: Zoo, read: Callable[[str], str]) -> None:
    name = read("Animal name: ").strip()
    food = read("Pantry food_id: ").strip()
    prep = _g_float(read, "Prep labour fee (AUD)", 6.5)
    animal = zoo.get_animal_by_name(name)
    print(zoo.feed_from_pantry(animal, food, prep))


def _adopt_menu(zoo: Zoo, read: Callable[[str], str]) -> None:
    from animals.factory import AnimalFactory

    print("Species keys:", ", ".join(sorted(AnimalFactory.supported_species().keys())))
    key = read("species_key: ").strip()
    name = read("Animal name: ").strip()
    pet = zoo.adopt_species(key, name)
    print(f"Welcome {pet.name} ({pet.__class__.__name__}) — placed in {zoo.habitat_of(pet)}.")


def _move_habitat(zoo: Zoo, read: Callable[[str], str]) -> None:
    name = read("Animal name: ").strip()
    label = read("Target habitat label: ").strip()
    animal = zoo.get_animal_by_name(name)
    print(zoo.assign_to_enclosure(animal, label))


def _restock_medicine_menu(zoo: Zoo, read: Callable[[str], str]) -> None:
    from systems.medicine_store import MedicineStore

    print("Catalog (key — label):")
    for med in MedicineStore().list_catalog_for_cli():
        print(f"  {med.key:10} {med.label}")
    key = read("medicine key: ").strip()
    doses = _g_int(read, "Doses to add", 5)
    print(zoo.purchase_medicine_doses(key, doses))


def _medicine_menu(zoo: Zoo, read: Callable[[str], str]) -> None:
    from systems.medicine_store import MedicineStore

    stock = MedicineStore().snapshot_stock()
    print("Doses on hand:", ", ".join(f"{k}={v}" for k, v in sorted(stock.items())))
    print("Treatments: vitamin, broad, fluid")
    key = read("medicine key: ").strip()
    name = read("Animal name: ").strip()
    animal = zoo.get_animal_by_name(name)
    print(zoo.apply_medicine(animal, key))


def _breed_menu(zoo: Zoo, read: Callable[[str], str]) -> None:
    a = read("Parent A name: ").strip()
    b = read("Parent B name: ").strip()
    hab = read("Habitat label (both parents must be listed there): ").strip()
    baby = read("Offspring name: ").strip()
    child = zoo.try_breed(a, b, hab, baby)
    print(f"New arrival: {child.name} ({child.__class__.__name__}).")


def _sounds_demo(zoo: Zoo) -> None:
    animals = zoo.list_animals()
    if not animals:
        print("No animals yet.")
        return
    for creature in animals:
        print(f"{creature.name}: {creature.make_sound()}")


def main() -> None:
    run_game_loop()


if __name__ == "__main__":
    main()
