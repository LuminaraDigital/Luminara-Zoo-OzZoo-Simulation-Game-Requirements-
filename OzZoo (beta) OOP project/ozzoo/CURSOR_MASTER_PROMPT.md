# OzZoo — Master Cursor Agent Prompt
## NIT2112 Object Oriented Programming | Victoria University | s8138393

---

## HOW TO USE THIS FILE

Paste each numbered prompt below into Cursor's **Agent chat** panel one at a time.
After each prompt, review the output, run the code, and move to the next.
Agent mode allows Cursor to read your entire codebase and edit multiple files
in a single turn — always use Agent mode (not Inline Edit) for prompts marked **[AGENT]**.

---

## PHASE 0 — PROJECT SETUP

### Prompt 0.1 — Project scaffold [AGENT]
```
Create a new Python project called "ozzoo" with the following directory structure:

ozzoo/
├── main.py
├── animals/
│   └── __init__.py
├── zoo/
│   └── __init__.py
├── systems/
│   └── __init__.py
├── ui/
│   └── __init__.py
└── hermes_integration/
    └── __init__.py

Then create a requirements.txt containing:
rich>=13.0

And a README.md with the title "OzZoo — Australian Wildlife Park Simulator" and a one-paragraph description.
```

### Prompt 0.2 — Git initialisation [AGENT]
```
In the terminal, run:
  git init
  git add .
  git commit -m "Initial scaffold for OzZoo NIT2112 assessment"

Then verify Python 3.11+ is available with: python --version
Install dependencies with: pip install rich
```

---

## PHASE 1 — EXCEPTION HIERARCHY

### Prompt 1.1 — Custom exceptions [AGENT]
```
In systems/exceptions.py, create the following custom exception hierarchy for OzZoo.
All exceptions must inherit from OzZooBaseException which extends Python's Exception.
Each exception must store an error_code string and a message, and call super().__init__()
with a formatted string of [error_code] message.

Required exceptions:
1. OzZooBaseException(Exception)     — error_code="OZ001"
2. InsufficientFundsError            — stores required and available floats; OZ002
3. InsufficientFoodError             — stores food_type, required, available; OZ003
4. InsufficientMedicineError         — stores medicine_type; OZ008
5. HabitatCapacityExceededError      — stores enclosure_name and capacity; OZ004
6. IncompatibleSpeciesError          — stores animal1, animal2, reason; OZ005
7. AnimalHealthCriticalError         — stores animal_name, health float; OZ006
8. InvalidEnclosureTypeError         — stores animal_species, required, provided; OZ007

Add APA-formatted module docstring crediting student Babatundji Williams-Fulwood s8138393,
unit NIT2112, Victoria University.
```

---

## PHASE 2 — ANIMAL HIERARCHY (Core OOP)

### Prompt 2.1 — IBreedable interface and Animal ABC [AGENT]
```
In animals/base.py, implement the following. Use Python's abc module throughout.

1. IBreedable(ABC) — interface with two abstract methods:
   - can_breed(self) -> bool
   - breed(self, partner) -> Optional[Animal]

2. Animal(IBreedable) — abstract root class with:
   CLASS CONSTANTS: BREED_HEALTH_MIN=70.0, BREED_HAPPINESS_MIN=60.0, CRITICAL_HEALTH=20.0
   INIT: assigns animal_id (8-char UUID), name, age=0, is_sick=False, enclosure=None
   NAME-MANGLED ATTRIBUTES: self.__health, self.__hunger, self.__happiness (all floats)
   PROPERTIES with setters that clamp to 0-100 range: health, hunger, happiness
   ABSTRACT PROPERTIES: species, habitat_type, purchase_price
   ABSTRACT METHODS: make_sound() -> str, get_dietary_needs() -> dict[str, float]
   CONCRETE METHODS:
     - tick() -> list[str]: age+=1, raise hunger by _hunger_rate(), reduce health if hunger>50,
       reduce happiness if health<50, 1% random illness chance. Returns list of event strings.
     - _hunger_rate() -> float: returns 8.0 (subclasses override)
     - eat(food_type, amount_kg) -> str: check dietary needs, calculate ratio, adjust hunger/happiness/health
     - administer_medicine(medicine_name) -> str: clear is_sick, restore health by 30, return status
     - can_breed() -> bool: health>=BREED_HEALTH_MIN, happiness>=BREED_HAPPINESS_MIN, age>=365, not sick
     - breed(partner) -> Optional[Animal]: same type check, 50% random success, return new instance of self's class
     - get_stats() -> AnimalStats: return named tuple/dataclass snapshot
     - __repr__: include class name, animal_id, name, health

Include an AnimalStats dataclass at the top of the file with fields:
name, species, health, hunger, happiness, age, is_sick.

Write full APA-formatted docstrings for every class and method.
```

### Prompt 2.2 — Mammal and Marsupial abstract classes [AGENT]
```
In animals/base.py, after the Animal class, add these abstract intermediate classes:

1. Mammal(Animal) — abstract, adds fur_type="Short", social_group_size=1,
   overrides _hunger_rate() to return 10.0. All 4 abstract properties and methods
   are still abstract (pass them down with @abstractmethod stubs).

2. Marsupial(Mammal) — abstract, adds pouch_young=0, fur_type="Thick",
   habitat_type property returns "Bush". Still abstract for species, purchase_price,
   make_sound, get_dietary_needs.

Then add these three concrete Marsupial subclasses:

3. Koala(Marsupial):
   species = "Koala", purchase_price = 8500.0
   _hunger_rate() = 5.0 (sleepy, slow metabolism)
   make_sound() = "{name} lets out a deep, bellowing snore."
   get_dietary_needs() = {"Eucalyptus": 1.5}
   tick() override: call super().tick(), if happiness<40 append enclosure cleaning suggestion

4. Kangaroo(Marsupial):
   habitat_type = "Savannah" (overrides Marsupial)
   species = "Eastern Grey Kangaroo", purchase_price = 3200.0
   social_group_size = 5, _hunger_rate() = 12.0
   make_sound() = "{name} stamps a powerful foot — THUMP!"
   get_dietary_needs() = {"Grass": 3.0, "Hay": 1.0}

5. Wombat(Marsupial):
   habitat_type = "Savannah"
   species = "Common Wombat", purchase_price = 4000.0, adds burrow_depth=0
   make_sound() = "{name} lets out a low, grumpy grunt."
   get_dietary_needs() = {"Grass": 2.0, "Roots": 0.5}
   tick() override: increment burrow_depth by random 1-5, every 30 days report depth

Add full docstrings with APA references to species facts.
```

### Prompt 2.3 — Bird and Reptile branches [AGENT]
```
In animals/base.py, add the remaining animal branches:

BIRD BRANCH:
1. Bird(Animal) — abstract, adds wing_span_cm=50.0, _hunger_rate()=7.0

2. FlightlessBird(Bird) — abstract, habitat_type="Savannah", adds running_speed_kmh=0.0

3. Emu(FlightlessBird):
   species="Emu", purchase_price=2800.0, running_speed_kmh=48.0, wing_span_cm=25.0
   make_sound() = "{name} makes a thunderous BOOMING drum sound."
   get_dietary_needs() = {"Seeds": 0.8, "Grass": 1.2, "Insects": 0.2}
   tick() override: 10% chance when happiness>70 to report visitor excitement

4. Raptor(Bird) — abstract, habitat_type="Aviary", territory_km2=10.0, _hunger_rate()=6.0

5. WedgeTailEagle(Raptor):
   species="Wedge-tailed Eagle", purchase_price=12000.0, wing_span_cm=230.0
   make_sound() = "{name} lets out a high, piercing KEEEE!"
   get_dietary_needs() = {"Raw Meat": 0.8}
   tick() override: when happiness>70 report visitor appeal boost

CANID BRANCH:
6. Canid(Mammal) — abstract, habitat_type="Savannah"
7. Dingo(Canid):
   species="Dingo", purchase_price=5500.0, pack_size=1
   incompatible_species = {"Koala", "Common Wombat"}  ← checked during enclosure placement
   make_sound() = "{name} raises its head and HOWLS into the night."
   get_dietary_needs() = {"Raw Meat": 1.5, "Bone": 0.3}, _hunger_rate()=13.0

REPTILE BRANCH:
8. Reptile(Animal) — abstract, is_ectotherm=True, preferred_temp_c=28.0, _hunger_rate()=4.0
9. Monitor(Reptile) — abstract, habitat_type="Reptile House", adds tongue_flicks=0
10. Goanna(Monitor):
    species="Lace Monitor (Goanna)", purchase_price=3500.0, preferred_temp_c=32.0
    make_sound() = "{name} flicks its tongue rapidly and hisses."
    get_dietary_needs() = {"Raw Meat": 0.6, "Eggs": 0.2}
    tick() override: increment tongue_flicks each day

Ensure every concrete class has a proper docstring including an APA-formatted reference
to a real scientific or government source about that species.
```

---

## PHASE 3 — DESIGN PATTERNS + RESOURCE SYSTEMS

### Prompt 3.1 — Observer pattern (EventBus + IObserver) [AGENT]
```
In systems/patterns.py, implement the Observer design pattern:

1. IObserver(ABC) — interface with one abstract method:
   on_event(self, event_type: str, payload: dict) -> None

2. EventBus — Singleton (via __new__ override) that is the Subject:
   _instance class variable
   _observers: dict[str, list[IObserver]]  initialised in __new__
   _event_log: list[dict]  class-level for session history
   Methods:
     get_instance() classmethod
     subscribe(event_type, observer): add to _observers[event_type]
     unsubscribe(event_type, observer): remove from _observers[event_type]
     publish(event_type, payload): append to _event_log, notify all subscribers
     get_log() -> list[dict]: return copy of _event_log

Include a docstring that identifies this as the Observer pattern and cites:
Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design patterns:
Elements of reusable object-oriented software. Addison-Wesley.
```

### Prompt 3.2 — Factory pattern (AnimalFactory) [AGENT]
```
In systems/patterns.py, after EventBus, implement the Factory pattern:

Module-level registry dict _SPECIES_REGISTRY mapping lower-case string keys
to concrete Animal classes. Include at minimum these entries:
"koala" → Koala, "kangaroo" → Kangaroo, "eastern grey kangaroo" → Kangaroo,
"wombat" → Wombat, "common wombat" → Wombat, "dingo" → Dingo,
"emu" → Emu, "wedge-tailed eagle" → WedgeTailEagle, "eagle" → WedgeTailEagle,
"goanna" → Goanna, "lace monitor (goanna)" → Goanna

AnimalFactory class with three static methods:
  create(species_name: str, individual_name: str) -> Animal
    Strip and lowercase the input, look up in registry.
    If not found, raise ValueError listing all available species.
  available_species() -> list[str]
    Return sorted, deduplicated list of species names (use temp instance to read species property)
  get_price(species_name: str) -> float
    Return purchase_price without full initialisation overhead.

Docstring must identify this as the Factory Method pattern with the Gamma et al. (1994) citation.
```

### Prompt 3.3 — Singleton FoodStore, MedicineStore, and Treasury [AGENT]
```
In systems/patterns.py, add three more classes:

1. FoodStore (Singleton via __new__):
   Class-level FOOD_PRICES dict:
     "Eucalyptus":4.50, "Grass":1.20, "Hay":0.80, "Seeds":2.00,
     "Insects":6.00, "Raw Meat":8.00, "Bone":3.00, "Roots":1.50, "Eggs":5.00
   Instance: _stock: dict[str, float] initialised to 10.0 kg each food type
   Methods:
     get_instance() classmethod
     stock() -> dict: copy of current stock
     purchase(food_type, kg, treasury) -> str: validate type, debit treasury, add to stock
     consume(food_type, kg) -> None: deduct stock, raise InsufficientFoodError if insufficient

2. MedicineStore (Singleton via __new__):
   Class-level MEDICINE_PRICES: "General Antibiotic":50, "Antifungal":75,
     "Wound Salve":30, "Vitamin Supplement":20
   Instance: _doses: dict[str, int] initialised to 5 each
   Methods: get_instance(), doses(), purchase(medicine, qty, treasury), use(medicine)
   use() raises InsufficientMedicineError if doses < 1

3. Transaction dataclass: description: str, amount: float, day: int

4. Treasury (not a singleton — one per Zoo instance):
   __init__(starting_balance=50000.0)
   _balance (private float), _ledger (list of Transaction), _day int
   balance property (read-only)
   set_day(day), credit(amount, description), debit(amount, description)
   debit() raises InsufficientFundsError if amount > balance
   get_ledger() -> list[Transaction], summary() -> str
```

---

## PHASE 4 — ZOO ENTITIES

### Prompt 4.1 — ICleanable interface, Enclosure, and Habitat [AGENT]
```
In zoo/entities.py, implement:

1. ICleanable(ABC) — interface:
   clean(self) -> str  (abstract)
   cleanliness property (abstract, float)

2. Enclosure(ICleanable):
   __init__(name, habitat_type, capacity=5)
   Attributes: name, habitat_type, _capacity, _animals list, __cleanliness=100.0,
     upgrade_level=0, maintenance_cost_per_day=50.0
   UPGRADE_COSTS class variable: [0, 5000, 12000, 25000]
   Properties: cleanliness (from __cleanliness), capacity (base + upgrade_level*2), animals (copy)
   ICleanable.clean(): restore __cleanliness to 100, boost animal happiness, return status string
   add_animal(animal) -> str:
     Check capacity (raise HabitatCapacityExceededError)
     Check habitat_type match (raise InvalidEnclosureTypeError)
     Check incompatible_species attr on animal against existing residents (raise IncompatibleSpeciesError)
     Append to _animals, set animal.enclosure = self.name
   remove_animal(animal) -> str
   tick() -> list[str]: degrade __cleanliness (2% + 3% per animal), health/happiness penalty if <20%
   upgrade(treasury) -> str: debit cost from treasury, increment upgrade_level, increase capacity
   visitor_appeal() -> float: weighted average of health(40%), happiness(40%), cleanliness(20%)

3. Habitat(ICleanable):
   __init__(name, description="")
   _enclosures list, __cleanliness=100.0
   add_enclosure(enclosure): append
   clean(): restore cleanliness, return status
   tick(): degrade 5%/day, warn if <30%
   total_visitor_appeal(): average appeal of all enclosures

4. Visitor:
   Class-level _visitor_count counter for unique IDs
   __init__(name=None, budget=None): auto-name, random budget 25-120
   __satisfaction (name-mangled), satisfaction property with 0-100 setter
   pay_admission(ticket_price) -> float: returns revenue or 0 if can't afford
   visit_enclosure(enclosure) -> float: update satisfaction based on appeal, return gift shop spend
   leave_review() -> str: 5-star rating system based on satisfaction
   donate() -> float: happy visitors (satisfaction>=75) donate 5-30 AUD

Write full APA-formatted docstrings and cite Gamma et al. (1994) for the Singleton pattern.
```

### Prompt 4.2 — Zoo Singleton (central orchestrator) [AGENT]
```
In zoo/entities.py, after Visitor, add the Zoo class as a Singleton:

Zoo (Singleton via __new__ with _initialised flag to prevent re-init):
INIT (only runs once):
  name, day=1, ticket_price=25.0
  _habitats, _all_enclosures, _all_animals (all lists)
  treasury = Treasury(starting_balance)
  food_store = FoodStore.get_instance()
  medicine_store = MedicineStore.get_instance()
  event_bus = EventBus.get_instance()
  reputation = 60.0, _daily_events list

get_instance() classmethod

MANAGEMENT METHODS:
  build_enclosure(name, habitat_type, capacity) -> Enclosure:
    Cost = 10000 + capacity * 500, debit treasury, create and store Enclosure

  purchase_animal(species, name, enclosure) -> str:
    Use AnimalFactory.create(), debit treasury for purchase_price, call enclosure.add_animal()

  feed_animal(animal, food_type, kg) -> str:
    Deduct from food_store, call animal.eat() — this IS the polymorphic call

  treat_animal(animal, medicine) -> str:
    Use medicine from medicine_store, call animal.administer_medicine()

  attempt_breeding(a1, a2) -> str:
    Call a1.breed(a2), register offspring in _all_animals if successful

ADVANCE_DAY() -> list[str]:
  For each animal: call tick(), check health <= CRITICAL_HEALTH → publish HEALTH_CRITICAL to EventBus
  Check health <= 0 → remove animal (death), reputation -= 5
  For each enclosure: call tick(), debit maintenance_cost_per_day
  For each habitat: call tick()
  Call _simulate_visitors() → collect revenue
  Compute reputation drift from average animal health
  Call _random_event() (10% chance: heatwave, media, excursion, quarantine, rain)
  Increment day, return all event strings

_simulate_visitors() -> int:
  base_visitors = int(reputation * 0.8) + random -5 to +10
  For each visitor: pay_admission, visit each enclosure, maybe donate
  Credit total revenue to treasury

PROPERTIES: all_animals, all_enclosures
LOOKUP: get_animal_by_name(), get_enclosure_by_name() (both case-insensitive)
```

---

## PHASE 5 — CLI GAME LOOP

### Prompt 5.1 — Observer: AlertObserver and CLI dashboard [AGENT]
```
In ui/cli.py, implement the following:

1. AlertObserver(IObserver):
   Implements on_event(): if event_type == "HEALTH_CRITICAL", print a bold red
   warning panel using Rich showing animal name and health percentage.

2. Helper functions using Rich (fallback to plain print if Rich not installed):
   display_banner(): ASCII art "OzZoo" title
   display_zoo_status(zoo): Rich Panel showing:
     - Finances panel: balance, ticket price, reputation, day
     - Animals panel: list of all animals with health/hunger/happiness color-coded
     - Enclosures panel: list of enclosures with occupancy, cleanliness, appeal
   display_animals(zoo): Rich Table with full animal stats

3. Menu action functions (each takes zoo as argument):
   menu_feed_animals(zoo), menu_buy_food(zoo), menu_buy_animal(zoo),
   menu_build_enclosure(zoo), menu_vet_clinic(zoo), menu_buy_medicine(zoo),
   menu_clean(zoo), menu_breeding(zoo), menu_set_ticket_price(zoo),
   menu_upgrade_enclosure(zoo), menu_animal_sounds(zoo), menu_ledger(zoo)
   
   Each function must catch OzZooBaseException and display the error cleanly.
   menu_animal_sounds() must call animal.make_sound() for every animal in the zoo
   — this is the explicit polymorphism demonstration.

4. MENU list of tuples: (key_string, label_string, function)
   Keys: 1-14 for actions, Q to quit.

5. run_game() function:
   Create Zoo("OzZoo", starting_balance=75000)
   Register AlertObserver with EventBus for "HEALTH_CRITICAL"
   Call setup_starter_zoo() to pre-populate
   Enter while True loop: display_zoo_status, print_menu, get input, dispatch to function

6. setup_starter_zoo(zoo): build 4 enclosures (Koala Korner/Bush, Roo Run/Savannah,
   Eagle's Roost/Aviary, Reptile House/Reptile House) and purchase 7 starter animals.
   Seed food store with starter stock.
```

---

## PHASE 6 — HERMES AGENT INTEGRATION

### Prompt 6.1 — Hermes skill file [AGENT]
```
In hermes_integration/skill.py, create a Hermes Agent skill module that exposes
OzZoo game functions for natural language control.

The file must:
1. Add the project root to sys.path so OzZoo modules can be imported from the Hermes skills directory
2. Define _get_zoo() helper that returns Zoo.get_instance() and seeds it if empty
3. Define _seed_zoo(zoo) that builds 2 starter enclosures and 3 animals, seeds food

Implement these Hermes-callable functions (each returns a JSON string):
  get_zoo_status() -> str: full zoo snapshot including all animals
  feed_animal(animal_name, food_type, amount_kg) -> str: look up animal, feed it
  advance_day() -> str: run zoo.advance_day(), return events and new day number
  get_sick_animals() -> str: list animals where is_sick == True
  treat_animal(animal_name, medicine) -> str: treat named animal
  buy_food(food_type, kg) -> str: purchase food from FoodStore
  list_available_species() -> str: all purchasable species with prices
  get_food_stock() -> str: current pantry levels
  make_animal_sound(animal_name) -> str: call animal.make_sound() (polymorphism demo)

Each function must have a Google-style docstring with:
  - Description
  - Args section
  - Returns section
  - Example Hermes prompt (e.g., '"Feed Kiki with 1.5 kg of Eucalyptus."')

All OzZooBaseException errors must be caught and returned as {"status": "error", "message": "..."}.

At the top of the file include the full Hermes setup instructions as a comment block:
  git clone https://github.com/NousResearch/hermes-agent.git
  cd hermes-agent && pip install -e ".[all,dev]"
  mkdir -p ~/.hermes/skills/ozzoo
  cp /path/to/ozzoo/hermes_integration/skill.py ~/.hermes/skills/ozzoo/
  hermes chat --toolsets skills

Cite: Nous Research. (2024). Hermes-Agent. GitHub. https://github.com/NousResearch/hermes-agent
```

---

## PHASE 7 — ENTRY POINT AND TESTING

### Prompt 7.1 — main.py [AGENT]
```
Create main.py in the project root with:
1. sys.path.insert to project root
2. Import run_game from ui.cli
3. if __name__ == "__main__": block that calls run_game() with KeyboardInterrupt handling
4. Full module docstring with student info, unit code, and pip install instructions

Then create a test_game.py integration test that:
- Resets all singletons (Zoo._instance, FoodStore._instance, etc.) for a clean test
- Creates a Zoo with $150,000 starting balance
- Builds 4 typed enclosures
- Purchases 6 animals across the enclosures
- Seeds the food store
- Feeds all animals polymorphically (same feed_animal() call for all types)
- Advances 3 days and asserts no crash
- Calls make_sound() on every animal (polymorphism assertion)
- Tests InsufficientFundsError, HabitatCapacityExceededError, InvalidEnclosureTypeError
- Tests AnimalFactory.available_species() returns >= 7 species
- Tests EventBus subscribe/publish with a TestObserver
- Tests Hermes skill get_zoo_status() returns valid JSON with status='success'
- Prints "ALL TESTS PASSED" on success
```

### Prompt 7.2 — Run and verify [AGENT]
```
In the terminal, run:
  python test_game.py

If any test fails, read the traceback carefully and fix the issue.
Common issues to check:
  1. MRO errors: Ensure Animal(IBreedable) not Animal(ABC, IBreedable)
  2. Habitat type mismatch: Kangaroo and Wombat must override habitat_type to "Savannah"
  3. Singleton not reset between tests: Reset _instance on Zoo, FoodStore, MedicineStore, EventBus
  4. InsufficientFunds in setup: Increase starting_balance or check enclosure build costs
  5. Animal species name casing: AnimalFactory registry uses .lower().strip()

Once tests pass, run the game with: python main.py
Verify: banner displays, starter zoo loads, menu responds, advancing a day prints events.
```

---

## PHASE 8 — DOCUMENTATION AND SUBMISSION

### Prompt 8.1 — Docstring audit [AGENT]
```
Read every .py file in this project and check that:
1. Every module has a module-level docstring with: description, author, student ID, unit, institution
2. Every class has a docstring explaining: purpose, attributes, OOP role (ABC/Singleton/etc.)
3. Every public method has a docstring with Args:, Returns:, Raises: sections
4. Every APA reference in a docstring uses the format:
   Author, A. A. (Year). Title in italics. Publisher. URL
5. The custom exceptions docstring explains the error_code convention

List any missing or incomplete docstrings and add them.
```

### Prompt 8.2 — UML generation [AGENT]
```
Read the entire codebase using @Codebase and generate a PlantUML class diagram
showing:
1. All abstract classes with <<abstract>> stereotype
2. All interfaces (ABCs with only abstract methods) with <<interface>> stereotype
3. All Singleton classes with <<singleton>> stereotype
4. Inheritance arrows (--|>) for all parent-child relationships
5. Association lines (-->) from Zoo to Enclosure, Animal, Treasury, FoodStore
6. Realisation arrows (..|>) from Enclosure→ICleanable, Habitat→ICleanable
7. Observer relationship: EventBus→IObserver→AlertObserver

Output the PlantUML @startuml ... @enduml code block.
```

### Prompt 8.3 — Create ZIP for submission [AGENT]
```
In the terminal, from the project root, run:
  find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; true
  find . -name "*.pyc" -delete 2>/dev/null; true
  cd ..
  zip -r ozzoo_s8138393_source_code.zip ozzoo/ \
    --exclude "ozzoo/.git/*" \
    --exclude "ozzoo/__pycache__/*"

Verify the zip was created and list its contents.
This is the file to submit as "Source Code" to the VU learning portal.
```

---

## QUICK REFERENCE — OOP REQUIREMENTS CHECKLIST

| Requirement | Implemented In | Status |
|---|---|---|
| ≥10 distinct classes | 14 named classes across animals/, zoo/, systems/ | ✅ |
| Encapsulation (__private) | Animal.__health/__hunger/__happiness | ✅ |
| Inheritance ≥2 levels | Animal→Mammal→Marsupial→Koala (4 levels) | ✅ |
| Polymorphism | Zoo.feed_animal(), make_sound() | ✅ |
| Abstract Base Class | Animal, IBreedable, ICleanable, IObserver | ✅ |
| Interface (ABC all-abstract) | IBreedable, ICleanable, IObserver | ✅ |
| Design Pattern | Observer (EventBus), Factory (AnimalFactory), Singleton (Zoo/FoodStore) | ✅ |
| Custom Exceptions | 8 exceptions in systems/exceptions.py | ✅ |
| Exception Handling | try/except in every user-facing method | ✅ |
| Game Loop | ui/cli.py run_game() with daily tick | ✅ |
| CLI Interface | Rich-powered dashboard in ui/cli.py | ✅ |
| Resource Management | FoodStore, MedicineStore, Treasury | ✅ |
| Animal Welfare | health/hunger/happiness decay, illness, death | ✅ |
| Breeding Mechanic | Animal.breed(), Zoo.attempt_breeding() | ✅ |
| Docstrings | All modules, classes, public methods | ✅ |
| UML Diagram | See Tutorial Documentation PDF | ✅ |
| AI Copilot Log | See AI Copilot Usage Log PDF | ✅ |
| APA 7th References | Throughout all docstrings and PDFs | ✅ |
| Hermes Integration | hermes_integration/skill.py | ✅ |

---

## CURSOR TIPS FOR BEST RESULTS

1. **Always use Agent mode** — click the Agent toggle before pasting any prompt. This lets Cursor read and edit the whole codebase in one pass.

2. **Use @Codebase** — after Phase 3, add `@Codebase` to the start of prompts so Cursor has full context:
   `@Codebase Review the Animal class hierarchy and confirm IBreedable is implemented correctly.`

3. **Pin key files** — use `@animals/base.py @zoo/entities.py` to focus Cursor on specific files when debugging.

4. **Checkpoint commits** — after each phase, commit so you can roll back:
   `git add . && git commit -m "Phase N complete"`

5. **Run tests after every phase** — `python test_game.py` catches integration issues early.

6. **If Cursor generates wrong imports** — always check that circular imports are avoided:
   - `exceptions.py` imports nothing from this project
   - `animals/base.py` imports only from `systems.exceptions`
   - `systems/patterns.py` imports from `animals.base` and `systems.exceptions`
   - `zoo/entities.py` imports from all three above
   - `ui/cli.py` imports from `zoo` and `systems`
