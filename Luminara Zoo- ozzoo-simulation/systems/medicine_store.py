"""Singleton vet cabinet with dose inventory (Tutorial: MedicineStore)."""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from systems.exceptions import InsufficientFundsError, InsufficientMedicineError, InvalidAmountError
from systems.medicine import Medicine, default_medicine_cabinet
from systems.treasury import Treasury


class MedicineStore:
    """Process-wide veterinary stock (Singleton — mirrors ``FoodStore`` design)."""

    __singleton_lock = threading.Lock()
    __instance: Optional["MedicineStore"] = None

    def __new__(cls) -> "MedicineStore":
        if cls.__instance is None:
            with cls.__singleton_lock:
                if cls.__instance is None:
                    cls.__instance = super().__new__(cls)
                    cls.__instance.__dict__["_MedicineStore__initialised"] = False
        return cls.__instance

    def __init__(self) -> None:
        if self.__initialised:
            return
        self.__cabinet: Dict[str, Medicine] = default_medicine_cabinet()
        self.__doses: Dict[str, int] = {k: 4 for k in self.__cabinet}
        self.__dict__["_MedicineStore__initialised"] = True

    @classmethod
    def reset_for_testing(cls) -> None:
        with cls.__singleton_lock:
            cls.__instance = None

    @property
    def __initialised(self) -> bool:
        return bool(self.__dict__.get("_MedicineStore__initialised", False))

    def cabinet(self) -> Dict[str, Medicine]:
        """Read-only mapping of treatment key to ``Medicine`` metadata."""
        return dict(self.__cabinet)

    def snapshot_stock(self) -> Dict[str, int]:
        """Copy of remaining doses per key."""
        return dict(self.__doses)

    def get_medicine(self, key: str) -> Medicine:
        k = key.lower().strip()
        if k not in self.__cabinet:
            raise KeyError(k)
        return self.__cabinet[k]

    def purchase_doses(self, medicine_key: str, doses: int, treasury: Treasury) -> str:
        """Restock the cabinet (debits treasury)."""
        try:
            if doses <= 0:
                raise InvalidAmountError("Dose quantity must be positive.", amount=float(doses))
            med = self.get_medicine(medicine_key)
            unit = max(12.0, round(med.cost_aud * 0.12, 2))
            total = round(unit * doses, 2)
            treasury.debit(total, context="medicine_restock")
            k = med.key
            self.__doses[k] = self.__doses.get(k, 0) + doses
            return f"Restocked {doses} dose(s) of {med.label} for ${total:.2f}."
        except KeyError:
            raise InsufficientMedicineError(
                f"Unknown medicine '{medicine_key}'.",
                medicine_key=medicine_key.lower().strip(),
            ) from None
        except (InsufficientFundsError, InvalidAmountError, InsufficientMedicineError):
            raise
        except Exception as exc:  # pragma: no cover
            raise InsufficientFundsError(
                "Unexpected error while restocking medicine.",
                cause=exc,
            ) from exc

    def consume_dose(self, medicine_key: str) -> Medicine:
        """Remove one dose before applying treatment; return the ``Medicine`` row."""
        med = self.get_medicine(medicine_key)
        k = med.key
        have = self.__doses.get(k, 0)
        if have < 1:
            raise InsufficientMedicineError(
                f"No doses of '{k}' left - restock the vet cabinet.",
                medicine_key=k,
                needed=1,
                available=have,
            )
        self.__doses[k] = have - 1
        return med

    def return_dose(self, medicine_key: str, quantity: int = 1) -> None:
        """Put doses back (e.g. treasury debit failed after ``consume_dose``)."""
        k = medicine_key.lower().strip()
        if k in self.__cabinet and quantity > 0:
            self.__doses[k] = self.__doses.get(k, 0) + int(quantity)

    def list_catalog_for_cli(self) -> List[Medicine]:
        return sorted(self.__cabinet.values(), key=lambda m: m.key)
