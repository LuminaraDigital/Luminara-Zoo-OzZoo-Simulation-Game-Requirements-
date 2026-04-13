"""
exceptions.py — Custom Exception Hierarchy for OzZoo Simulation Game.

All application-specific errors are derived from OzZooBaseException so
callers can choose to catch the whole family or individual subtypes.

Author : Babatundji Williams-Fulwood
Student ID : s8138393
Unit : NIT2112 Object Oriented Programming — Victoria University
"""


class OzZooBaseException(Exception):
    """
    Root exception for every OzZoo-specific error.

    Wraps a human-readable message with a unique error code so that the
    CLI can display consistent, structured feedback.

    Attributes:
        error_code (str): Short alphanumeric identifier (e.g. "OZ002").
        message    (str): Plain-English description of what went wrong.
    """

    def __init__(self, message: str, error_code: str = "OZ001") -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(f"[{error_code}] {message}")


# ---------------------------------------------------------------------------
# Financial errors
# ---------------------------------------------------------------------------

class InsufficientFundsError(OzZooBaseException):
    """
    Raised when the zoo's treasury cannot cover a transaction.

    Args:
        required  (float): Dollar amount the operation costs.
        available (float): Current balance in the zoo's account.
    """

    def __init__(self, required: float, available: float) -> None:
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient funds — need ${required:,.2f} but only ${available:,.2f} available.",
            "OZ002",
        )


# ---------------------------------------------------------------------------
# Resource errors
# ---------------------------------------------------------------------------

class InsufficientFoodError(OzZooBaseException):
    """
    Raised when the food store cannot supply an animal's meal.

    Args:
        food_type (str): The food variety that is short (e.g. "Eucalyptus").
        required  (int): Kilograms needed.
        available (int): Kilograms currently in stock.
    """

    def __init__(self, food_type: str, required: float, available: float) -> None:
        self.food_type = food_type
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient {food_type}: need {required:.1f} kg but only {available:.1f} kg in stock.",
            "OZ003",
        )


class InsufficientMedicineError(OzZooBaseException):
    """Raised when the veterinary cabinet has run out of a medicine type."""

    def __init__(self, medicine_type: str) -> None:
        self.medicine_type = medicine_type
        super().__init__(
            f"No {medicine_type} left in the veterinary cabinet — purchase more supplies.",
            "OZ008",
        )


# ---------------------------------------------------------------------------
# Habitat / enclosure errors
# ---------------------------------------------------------------------------

class HabitatCapacityExceededError(OzZooBaseException):
    """
    Raised when an enclosure is full and another animal is placed in it.

    Args:
        enclosure_name (str): Display name of the enclosure.
        capacity       (int): Maximum animals the enclosure supports.
    """

    def __init__(self, enclosure_name: str, capacity: int) -> None:
        self.enclosure_name = enclosure_name
        self.capacity = capacity
        super().__init__(
            f"'{enclosure_name}' is at full capacity ({capacity} animals). Build an upgrade first.",
            "OZ004",
        )


class IncompatibleSpeciesError(OzZooBaseException):
    """
    Raised when two animals with conflicting behaviours share an enclosure.

    Args:
        animal1 (str): Name / species of the first animal.
        animal2 (str): Name / species of the second animal.
        reason  (str): Plain-English explanation of the conflict.
    """

    def __init__(self, animal1: str, animal2: str, reason: str) -> None:
        self.animal1 = animal1
        self.animal2 = animal2
        super().__init__(
            f"Incompatible species: {animal1} and {animal2} cannot share a habitat — {reason}.",
            "OZ005",
        )


class InvalidEnclosureTypeError(OzZooBaseException):
    """Raised when an animal is placed in a structurally wrong enclosure type."""

    def __init__(
        self, animal_species: str, required_habitat: str, provided_habitat: str
    ) -> None:
        super().__init__(
            f"{animal_species} needs a '{required_habitat}' enclosure, "
            f"not a '{provided_habitat}' enclosure.",
            "OZ007",
        )


# ---------------------------------------------------------------------------
# Animal welfare errors
# ---------------------------------------------------------------------------

class AnimalHealthCriticalError(OzZooBaseException):
    """
    Raised (and observed by the EventSystem) when health falls below 20 %.

    Args:
        animal_name (str):  The animal's display name.
        health      (float): Current health percentage (0–100).
    """

    def __init__(self, animal_name: str, health: float) -> None:
        self.animal_name = animal_name
        self.health = health
        super().__init__(
            f"CRITICAL HEALTH ALERT — {animal_name} is at {health:.1f}% health! "
            "Administer medicine immediately.",
            "OZ006",
        )
