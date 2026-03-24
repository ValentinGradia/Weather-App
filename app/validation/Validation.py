from datetime import datetime
from main import geolocator, geocode

class UserInputDestinationValidation:

	@staticmethod
	#Parse a YYYY-MM-DD date and throw a ValueError if invalid.
	def _parse_iso_date(date_value, field_name):
		try:
			return datetime.strptime(date_value, "%Y-%m-%d").date()
		except (TypeError, ValueError):
			raise ValueError(f"{field_name} must be in YYYY-MM-DD format")
		
	@staticmethod
	#Validate start/end dates and return parsed date objects.
	def _validate_date_range(start_date_raw, end_date_raw):
		start_date = UserInputDestinationValidation._parse_iso_date(start_date_raw, "start_date")
		end_date = UserInputDestinationValidation._parse_iso_date(end_date_raw, "end_date")

		if start_date > end_date:
			raise ValueError("start_date must be before or equal to end_date")

		if (end_date - start_date).days > 31:
			raise ValueError("date range cannot exceed 31 days")

		return start_date, end_date
	
	@staticmethod
	def _handle_location(location, value_location):
		"""Resolve location input according to its type (GPS, name, or postal code)."""
		place = None
		match location:
			case "GPS Coordinates":
				place = geolocator.reverse(value_location)
			case "City" | "Town" | "Country":
				place = geocode(value_location)
			case "Postal code" | "Postal Code" | "Zip Code":
				# Help Nominatim interpret numeric zip inputs more reliably.
				place = geocode(f"{value_location} postal code")
				if place is None:
					place = geocode(value_location)
			case _:
				place = geocode(value_location)

		return place

