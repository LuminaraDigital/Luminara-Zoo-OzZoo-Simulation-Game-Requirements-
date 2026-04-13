"""Stock-keeping unit for pantry items (assessment: Food resource class)."""

from __future__ import annotations


class FoodItem:
    """Describes a purchasable food line item used by multiple species."""

    def __init__(
        self,
        food_id: str,
        display_name: str,
        unit_price_aud: float,
        category: str,
    ) -> None:
        """Create a catalog entry.

        Args:
            food_id: Normalised token matching ``Animal.eat`` inputs (e.g. ``grass``).
            display_name: Human-readable shelf label for the CLI.
            unit_price_aud: Cost per unit in Australian dollars.
            category: Rough diet class (herbivore, carnivore, omnivore, reptile).
        """
        self.__food_id = self._validate_id(food_id)
        self.__display_name = display_name.strip() or self.__food_id
        if unit_price_aud <= 0:
            raise ValueError("Food unit price must be positive.")
        self.__unit_price_aud = round(float(unit_price_aud), 2)
        self.__category = category.strip() or "general"

    @staticmethod
    def _validate_id(food_id: str) -> str:
        token = food_id.lower().strip()
        if not token:
            raise ValueError("food_id must be non-empty.")
        return token

    @property
    def food_id(self) -> str:
        return self.__food_id

    @property
    def display_name(self) -> str:
        return self.__display_name

    @property
    def unit_price_aud(self) -> float:
        return self.__unit_price_aud

    @property
    def category(self) -> str:
        return self.__category
