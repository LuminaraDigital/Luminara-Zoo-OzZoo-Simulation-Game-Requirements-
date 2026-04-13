"""Treasury subsystem: encapsulated zoo finances with explicit error handling.

References:
    Gamma et al. (1994) for separating concerns and stable abstractions.
    Martin (2017) for keeping domain rules (money invariants) near the core.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, List

from systems.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    OzZooBaseException,
)


def _round_money(value: float) -> float:
    """Round currency to two decimal places for stable comparisons."""
    return round(float(value), 2)


class Treasury:
    """Tracks cash on hand for the zoo with validated deposits and withdrawals.

    Invariants:
        Balance is never negative after a successful operation.
        All amounts must be strictly positive for credit/debit calls.
    """

    def __init__(self, opening_balance: float = 10_000.0) -> None:
        """Create a treasury with a non-negative opening balance.

        Args:
            opening_balance: Starting funds in dollars.

        Raises:
            InvalidAmountError: If ``opening_balance`` is negative.
        """
        try:
            if opening_balance < 0:
                raise InvalidAmountError(
                    "Opening balance cannot be negative.",
                    amount=opening_balance,
                )
            self.__balance = _round_money(opening_balance)
            self.__ledger: Deque[dict[str, Any]] = deque(maxlen=15)
            self.__ledger.append(
                {
                    "kind": "open",
                    "amount": self.__balance,
                    "context": "opening_balance",
                    "balance_after": self.__balance,
                }
            )
        except InvalidAmountError:
            raise
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise InvalidAmountError(
                "Failed to initialize treasury balance.",
                amount=opening_balance,
                cause=exc,
            ) from exc

    def ledger_entries(self) -> List[dict[str, Any]]:
        """Last ledger rows (newest last), capped for the in-game financial review."""
        return list(self.__ledger)

    @property
    def balance(self) -> float:
        """Current cash balance (read-only via property)."""
        return _round_money(self.__balance)

    def credit(self, amount: float, *, context: str = "credit") -> float:
        """Add funds to the treasury.

        Args:
            amount: Dollars to add; must be positive.
            context: Label for auditing or error messages.

        Returns:
            The new balance after crediting.

        Raises:
            InvalidAmountError: If ``amount`` is not positive.
        """
        try:
            if amount <= 0:
                raise InvalidAmountError(
                    f"Credit amount must be positive ({context}).",
                    amount=amount,
                )
            self.__balance = _round_money(self.__balance + amount)
            self.__ledger.append(
                {
                    "kind": "credit",
                    "amount": amount,
                    "context": context,
                    "balance_after": self.balance,
                }
            )
            return self.balance
        except InvalidAmountError:
            raise
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise InvalidAmountError(
                "Unexpected failure while crediting treasury.",
                amount=amount,
                cause=exc,
            ) from exc

    def debit(self, amount: float, *, context: str = "debit") -> float:
        """Subtract funds if the balance can cover the debit.

        Args:
            amount: Dollars to remove; must be positive.
            context: Label for auditing or error messages.

        Returns:
            The new balance after debiting.

        Raises:
            InvalidAmountError: If ``amount`` is not positive.
            InsufficientFundsError: If ``amount`` exceeds ``balance``.
        """
        try:
            if amount <= 0:
                raise InvalidAmountError(
                    f"Debit amount must be positive ({context}).",
                    amount=amount,
                )
            if amount > self.__balance + 1e-9:
                raise InsufficientFundsError(
                    f"Insufficient funds for {context}.",
                    required=amount,
                    available=self.balance,
                )
            self.__balance = _round_money(self.__balance - amount)
            self.__ledger.append(
                {
                    "kind": "debit",
                    "amount": amount,
                    "context": context,
                    "balance_after": self.balance,
                }
            )
            return self.balance
        except (InvalidAmountError, InsufficientFundsError):
            raise
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise OzZooTreasuryOperationError(
                "Unexpected failure while debiting treasury.",
                cause=exc,
            ) from exc

    def can_afford(self, amount: float) -> bool:
        """Return True if the treasury can cover ``amount`` without going negative."""
        try:
            if amount <= 0:
                return True
            return _round_money(amount) <= self.balance + 1e-9
        except Exception:
            return False


class OzZooTreasuryOperationError(OzZooBaseException):
    """Raised when an unexpected failure occurs during treasury operations."""

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message, cause=cause)
