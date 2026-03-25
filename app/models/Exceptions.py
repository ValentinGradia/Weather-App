class ValidationError(ValueError):
	"""Base class for validation-related errors."""


class DateLengthValidationError(ValidationError):
	"""Raised when a provided date does not have expected length."""


class DateFormatValidationError(ValidationError):
	"""Raised when a provided date is not in an accepted format."""


class DateRangeOrderValidationError(ValidationError):
	"""Raised when start_date is greater than end_date."""


class DateRangeLimitValidationError(ValidationError):
	"""Raised when requested date range exceeds allowed size."""
