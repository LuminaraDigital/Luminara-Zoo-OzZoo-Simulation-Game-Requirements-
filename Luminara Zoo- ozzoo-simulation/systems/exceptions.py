"""Custom exception hierarchy for Luminara Zoo (project); root class name kept as
``OzZooBaseException`` for consistency with submitted Tutorial / AI log PDFs.

References:
    Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns:
    Elements of reusable object-oriented software*. Addison-Wesley.

    Martin, R. C. (2017). *Clean architecture: A craftsman's guide to software
    structure and design*. Prentice Hall.
"""

from __future__ import annotations


class OzZooBaseException(Exception):
    """Root exception for all Luminara Zoo domain errors (name retained for PDFs).

    Subclasses isolate failure modes (treasury, enclosures, feeding) so
    callers can handle them explicitly without catching bare ``Exception``.
    """

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        """Initialize the exception with a user-facing message.

        Args:
            message: Human-readable description of the failure.
            cause: Optional underlying exception for exception chaining.
        """
        super().__init__(message)
        self.__cause = cause

    @property
    def cause(self) -> BaseException | None:
        """Optional chained cause preserved for diagnostics."""
        return self.__cause


class InsufficientFundsError(OzZooBaseException):
    """Raised when a debit would drop the treasury balance below zero."""

    def __init__(
        self,
        message: str,
        *,
        required: float | None = None,
        available: float | None = None,
        cause: BaseException | None = None,
    ) -> None:
        """Attach optional monetary context for logging or UI display.

        Args:
            message: Description of the shortfall.
            required: Amount that was requested.
            available: Balance available at the time of the attempt.
            cause: Optional chained exception.
        """
        super().__init__(message, cause=cause)
        self.__required = required
        self.__available = available

    @property
    def required(self) -> float | None:
        """Monetary amount that was required for the operation."""
        return self.__required

    @property
    def available(self) -> float | None:
        """Treasury balance available when the operation was attempted."""
        return self.__available


class InvalidAmountError(OzZooBaseException):
    """Raised for non-positive or otherwise invalid monetary amounts."""

    def __init__(
        self,
        message: str,
        *,
        amount: float | None = None,
        cause: BaseException | None = None,
    ) -> None:
        """Record the offending amount when supplied.

        Args:
            message: Explanation of why the amount is invalid.
            amount: The value that failed validation.
            cause: Optional chained exception.
        """
        super().__init__(message, cause=cause)
        self.__amount = amount

    @property
    def amount(self) -> float | None:
        """Invalid amount associated with this error."""
        return self.__amount


class CapacityExceededError(OzZooBaseException):
    """Raised when an enclosure or zoo-wide capacity limit would be exceeded."""

    def __init__(
        self,
        message: str,
        *,
        limit: int | None = None,
        attempted_total: int | None = None,
        cause: BaseException | None = None,
    ) -> None:
        """Capture capacity context for reporting.

        Args:
            message: Description of the capacity violation.
            limit: Maximum allowed occupants or units.
            attempted_total: Total that would exist after the operation.
            cause: Optional chained exception.
        """
        super().__init__(message, cause=cause)
        self.__limit = limit
        self.__attempted_total = attempted_total

    @property
    def limit(self) -> int | None:
        """Configured capacity limit."""
        return self.__limit

    @property
    def attempted_total(self) -> int | None:
        """Population count that would have resulted from the operation."""
        return self.__attempted_total


class InvalidCapacityError(OzZooBaseException):
    """Raised when zoo capacity configuration is not a positive integer."""

    def __init__(
        self,
        message: str,
        *,
        capacity: int | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.__capacity = capacity

    @property
    def capacity(self) -> int | None:
        """Invalid capacity value supplied by the caller."""
        return self.__capacity


class AnimalNotFoundError(OzZooBaseException):
    """Raised when an animal identifier does not match a resident."""

    pass


class FeedingError(OzZooBaseException):
    """Raised when feeding constraints cannot be satisfied."""

    pass


class InsufficientFoodError(OzZooBaseException):
    """Raised when the pantry cannot cover a feeding or purchase request."""

    def __init__(
        self,
        message: str,
        *,
        food_id: str | None = None,
        needed: int | None = None,
        available: int | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.__food_id = food_id
        self.__needed = needed
        self.__available = available

    @property
    def food_id(self) -> str | None:
        return self.__food_id

    @property
    def needed(self) -> int | None:
        return self.__needed

    @property
    def available(self) -> int | None:
        return self.__available


class IncompatibleSpeciesError(OzZooBaseException):
    """Raised when an animal cannot be placed in the chosen habitat."""

    def __init__(
        self,
        message: str,
        *,
        family: str | None = None,
        enclosure: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.__family = family
        self.__enclosure = enclosure

    @property
    def family(self) -> str | None:
        return self.__family

    @property
    def enclosure(self) -> str | None:
        return self.__enclosure


class BreedingFailedError(OzZooBaseException):
    """Raised when breeding prerequisites are not satisfied."""

    pass


class HabitatNotFoundError(OzZooBaseException):
    """Raised when a habitat label does not exist."""

    pass


class InsufficientMedicineError(OzZooBaseException):
    """Raised when the vet cabinet has no doses of the requested treatment."""

    def __init__(
        self,
        message: str,
        *,
        medicine_key: str | None = None,
        needed: int | None = None,
        available: int | None = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, cause=cause)
        self.__medicine_key = medicine_key
        self.__needed = needed
        self.__available = available

    @property
    def medicine_key(self) -> str | None:
        return self.__medicine_key

    @property
    def needed(self) -> int | None:
        return self.__needed

    @property
    def available(self) -> int | None:
        return self.__available
