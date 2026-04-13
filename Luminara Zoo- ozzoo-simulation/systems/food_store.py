"""Singleton pantry for assorted feed types (Factory + resource management)."""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from systems.exceptions import InsufficientFundsError, InsufficientFoodError, InvalidAmountError
from systems.food_item import FoodItem
from systems.treasury import Treasury


class FoodStore:
    """Process-wide food inventory (Singleton — one ledger per game runtime)."""

    __singleton_lock = threading.Lock()
    __instance: Optional["FoodStore"] = None

    def __new__(cls) -> "FoodStore":
        if cls.__instance is None:
            with cls.__singleton_lock:
                if cls.__instance is None:
                    cls.__instance = super().__new__(cls)
                    cls.__instance.__dict__["_FoodStore__initialised"] = False
        return cls.__instance

    def __init__(self) -> None:
        if self.__initialised:
            return
        self.__catalog: Dict[str, FoodItem] = {}
        self.__inventory: Dict[str, int] = {}
        self._register_default_catalog()
        self.__dict__["_FoodStore__initialised"] = True

    @classmethod
    def reset_for_testing(cls) -> None:
        """Release the singleton (unit tests only)."""
        with cls.__singleton_lock:
            cls.__instance = None

    @property
    def __initialised(self) -> bool:
        return bool(self.__dict__.get("_FoodStore__initialised", False))

    def _register_default_catalog(self) -> None:
        """Seed purchasable foods aligned with species diets."""
        items = [
            FoodItem("eucalyptus", "Eucalyptus browse bale", 22.0, "herbivore"),
            FoodItem("browse", "Mixed browse bundle", 20.0, "herbivore"),
            FoodItem("grass", "Irrigated pasture hay", 14.0, "herbivore"),
            FoodItem("hay", "Lucerne hay bale", 16.0, "herbivore"),
            FoodItem("pellets", "Macropod pellets", 19.0, "herbivore"),
            FoodItem("roots", "Wombat root vegetable mix", 17.0, "herbivore"),
            FoodItem("grain", "Emu grain mix", 15.0, "omnivore"),
            FoodItem("greens", "Chopped greens", 12.0, "omnivore"),
            FoodItem("insects", "Calcium-dusted insects", 28.0, "protein"),
            FoodItem("fruit", "Fruit medley", 18.0, "omnivore"),
            FoodItem("meat", "Kangaroo mince / raptor meat", 32.0, "carnivore"),
            FoodItem("carcass", "Whole prey carcass", 55.0, "carnivore"),
            FoodItem("bones", "Recreational bones", 25.0, "carnivore"),
            FoodItem("prey", "Quail / rabbit prey item", 48.0, "carnivore"),
            FoodItem("eggs", "Protein eggs", 14.0, "omnivore"),
        ]
        for it in items:
            self.__catalog[it.food_id] = it
            self.__inventory.setdefault(it.food_id, 0)
        # Opening-day pantry so new managers are not soft-locked before first shop run.
        starter = {
            "eucalyptus": 6,
            "grass": 8,
            "meat": 6,
            "grain": 6,
            "insects": 5,
        }
        for sid, qty in starter.items():
            self.__inventory[sid] = self.__inventory.get(sid, 0) + qty

    def list_catalog(self) -> List[FoodItem]:
        """Return catalog entries sorted by id."""
        return sorted(self.__catalog.values(), key=lambda x: x.food_id)

    def snapshot_inventory(self) -> dict[str, int]:
        """Copy of current stock levels."""
        return dict(self.__inventory)

    def purchase(self, food_id: str, quantity: int, treasury: Treasury) -> str:
        """Buy units using the zoo treasury.

        Args:
            food_id: Catalog token.
            quantity: Number of units to add.
            treasury: Active ``Treasury`` instance to debit.

        Returns:
            Confirmation string for the CLI.

        Raises:
            InvalidAmountError: Bad quantity.
            InsufficientFundsError: Cannot afford the order.
        """
        try:
            if quantity <= 0:
                raise InvalidAmountError("Purchase quantity must be positive.", amount=float(quantity))
            fid = food_id.lower().strip()
            if fid not in self.__catalog:
                raise InsufficientFoodError(f"Unknown food item '{food_id}'.", food_id=fid)
            item = self.__catalog[fid]
            total = round(item.unit_price_aud * quantity, 2)
            treasury.debit(total, context="food_purchase")
            self.__inventory[fid] = self.__inventory.get(fid, 0) + quantity
            return f"Purchased {quantity}× {item.display_name} for ${total:.2f}."
        except (InsufficientFundsError, InvalidAmountError, InsufficientFoodError):
            raise
        except Exception as exc:  # pragma: no cover
            raise InsufficientFundsError(
                "Unexpected error purchasing food.",
                required=None,
                available=treasury.balance,
                cause=exc,
            ) from exc

    def restock(self, food_id: str, quantity: int = 1) -> None:
        """Return units to inventory (e.g. rollback after a rejected meal)."""
        fid = food_id.lower().strip()
        self.__inventory[fid] = self.__inventory.get(fid, 0) + max(0, int(quantity))

    def consume(self, food_id: str, quantity: int = 1) -> None:
        """Remove stock for feeding.

        Raises:
            InsufficientFoodError: If not enough units on hand.
        """
        try:
            if quantity <= 0:
                raise InvalidAmountError("Consume quantity must be positive.", amount=float(quantity))
            fid = food_id.lower().strip()
            have = self.__inventory.get(fid, 0)
            if have < quantity:
                raise InsufficientFoodError(
                    f"Not enough '{fid}' in pantry (have {have}, need {quantity}).",
                    food_id=fid,
                    needed=quantity,
                    available=have,
                )
            self.__inventory[fid] = have - quantity
        except InsufficientFoodError:
            raise
        except InvalidAmountError:
            raise
        except Exception as exc:  # pragma: no cover
            raise InsufficientFoodError(
                "Unexpected pantry error.",
                food_id=food_id,
                cause=exc,
            ) from exc
