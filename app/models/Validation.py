from datetime import datetime, timedelta
from app.services.Opencage import geocoder
from app.models.Exceptions import (
	DateFormatValidationError,
	DateLengthValidationError,
	DateRangeLimitValidationError,
	DateRangeOrderValidationError,
)

class UserInputDestinationValidation:
	@staticmethod
	#Ensure date values are exactly 10 characters (YYYY-MM-DD or YYYY/MM/DD).
	def _validate_date_length(date_value, field_name):
		if not isinstance(date_value, str) or len(date_value) != 10:
			raise DateLengthValidationError(f"{field_name} must have exactly 10 characters")

	@staticmethod
	#Parse a date string and throw a specific validation error if invalid.
	def _parse_iso_date(date_value, field_name):
		UserInputDestinationValidation._validate_date_length(date_value, field_name)

		for date_format in ("%Y-%m-%d", "%Y/%m/%d"):
			try:
				return datetime.strptime(date_value, date_format).date()
			except (TypeError, ValueError):
				continue

		raise DateFormatValidationError(
			f"{field_name} must be in YYYY-MM-DD or YYYY/MM/DD format"
		)
		
	@staticmethod
	#Validate start/end dates and return parsed date objects.
	def _validate_date_range(start_date_raw, end_date_raw):
		start_date = UserInputDestinationValidation._parse_iso_date(start_date_raw, "start_date")
		end_date = UserInputDestinationValidation._parse_iso_date(end_date_raw, "end_date")

		if start_date > end_date:
			raise DateRangeOrderValidationError("start_date must be before or equal to end_date")

		if (end_date - start_date).days > 31:
			raise DateRangeLimitValidationError("date range cannot exceed 31 days")

		return start_date, end_date

	@staticmethod
	#Return every date between start and end, including both boundaries.
	def get_all_dates_between(start_date_raw, end_date_raw):
		start_date, end_date = UserInputDestinationValidation._validate_date_range(
			start_date_raw,
			end_date_raw,
		)

		total_days = (end_date - start_date).days + 1
		return [
			(start_date + timedelta(days=offset)).isoformat()
			for offset in range(total_days)
		]
	
	@staticmethod
	def _handle_location(location):
		place = geocoder.geocode(location)
		return place

