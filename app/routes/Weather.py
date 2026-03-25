import json
from app.models.Validation import UserInputDestinationValidation
from urllib.request import urlopen
from app.models.Temperature import Temperature
from datetime import datetime

from flask import Blueprint, jsonify, request

from main import db
from app.models.Destination import Destination


weather_bp = Blueprint("weather", __name__)



def _read_json_response(url):
	"""Fetch and decode JSON payload from an HTTP endpoint."""
	with urlopen(url, timeout=10) as response:
		return json.loads(response.read().decode("utf-8"))



def _destination_to_response(destination):
	"""Convert a Destination database row into a full API response payload."""
	payload = {}
	if destination.description:
		try:
			payload = json.loads(destination.description)
		except json.JSONDecodeError:
			payload = {"raw_description": destination.description}

	payload["id"] = destination.id
	payload["weather"] = destination.weather
	return payload


#CREATE: Validate input, fetch weather, and persist location/date-range weather request.
@weather_bp.route("/destinations", methods=["POST"])
def create_destination():
	data = request.get_json()
	location = data.get("location")
	start_date = data.get("start_date")
	end_date = data.get("end_date")

	if not location or not start_date or not end_date:
		return jsonify({"error": "location, start_date and end_date are required"}), 400
	try:
		resolved_location = UserInputDestinationValidation._handle_location(location)
	except Exception:
		return jsonify({"error": "failed to resolve location"}), 500

	if not resolved_location:
		return jsonify({"error": "location not found"}), 400
	
	coordinates = resolved_location[0].get("geometry", {})
	lat = coordinates.get("lat")
	lon = coordinates.get("lng")

	location_formatted = resolved_location[0]['formatted']

	if Destination.already_exists(location_formatted, start_date, end_date):
		return jsonify({"error": "location already stored for this date range"}), 409
	
	temperatures_in_location_between_dates = []
	try:
		range_dates = UserInputDestinationValidation.get_all_dates_between(start_date, end_date)
	except ValueError as exc:
		return jsonify({"error": str(exc)}), 400
	
	#Creation of our models
	destination = Destination(location_formatted)

	#We store our destination
	db.session.add(destination)
	db.session.flush()

	for date in range_dates:
		temperature_response = Temperature.get_temperature(lat, lon, date)
		date_casted = datetime.strptime(date, "%Y-%m-%d").date()

		temperature = Temperature(destination.id, date_casted, temperature_response["morning"][:4], 
							temperature_response["afternoon"][:4], temperature_response["night"][:4])
		
		#We store our temperature
		db.session.add(temperature)
		temperatures_in_location_between_dates.append(
			{
				"date": date,
				"temperatures": temperature_response,
			}
		)

	db.session.commit()

	return jsonify(
		{
			"id location": destination.id,
			"location": location_formatted,
			"weather": temperatures_in_location_between_dates,
		}
	), 200


#READ: Return all stored weather requests from the database
@weather_bp.route("/destinations", methods=["GET"])
def get_destinations():
	# destinations = Destination.query.all()
	data = request.get_json()
	location = data.get("location")
	start_date = data.get("start_date")
	end_date = data.get("end_date")

	try:
		resolved_location = UserInputDestinationValidation._handle_location(location)
	except Exception:
		return jsonify({"error": "failed to resolve location"}), 500
	
	destinations = Destination.query.get()
	
	# return jsonify([_destination_to_response(destination) for destination in destinations]), 200


@weather_bp.route("/destinations/<int:destination_id>", methods=["GET"])
def get_destination(destination_id):
	"""READ: Return one stored weather request by its database ID."""
	destination = Destination.query.get(destination_id)
	if not destination:
		return jsonify({"error": "destination not found"}), 404

	return jsonify(_destination_to_response(destination)), 200


# @app.route("/destinations/<int:destination_id>", methods=["PUT", "PATCH"])
# def update_destination(destination_id):
# 	"""UPDATE: Revalidate editable fields, refresh weather data, and persist updates."""
# 	destination = Destination.query.get(destination_id)
# 	if not destination:
# 		return jsonify({"error": "destination not found"}), 404

# 	current_payload = _destination_to_response(destination)
# 	current_location = current_payload.get("location", {})
# 	current_dates = current_payload.get("date_range", {})

# 	data = request.get_json(silent=True) or {}
# 	location = data.get("location", current_location.get("requested", destination.weather))
# 	start_date = data.get("start_date", current_dates.get("start_date"))
# 	end_date = data.get("end_date", current_dates.get("end_date"))

# 	if not location or not start_date or not end_date:
# 		return jsonify({"error": "location, start_date and end_date are required"}), 400

# 	try:
# 		start, end = UserInputDestinationValidation._validate_date_range(start_date, end_date)
# 	except ValueError as exc:
# 		return jsonify({"error": str(exc)}), 400

# 	resolved_location = _resolve_location(location)
# 	if not resolved_location:
# 		return jsonify({"error": "location not found"}), 400

# 	temperatures = _fetch_temperatures(
# 		resolved_location["latitude"],
# 		resolved_location["longitude"],
# 		start.isoformat(),
# 		end.isoformat(),
# 	)

# 	updated_payload = {
# 		"location": {
# 			"requested": location,
# 			"resolved_name": resolved_location.get("name"),
# 			"country": resolved_location.get("country"),
# 			"latitude": resolved_location.get("latitude"),
# 			"longitude": resolved_location.get("longitude"),
# 		},
# 		"date_range": {
# 			"start_date": start.isoformat(),
# 			"end_date": end.isoformat(),
# 		},
# 		"temperatures": temperatures,
# 	}

# 	destination.weather = resolved_location.get("name", location)
# 	destination.description = json.dumps(updated_payload)
# 	db.session.commit()

# 	return jsonify(_destination_to_response(destination)), 200


@weather_bp.route("/destinations/<int:destination_id>", methods=["DELETE"])
def delete_destination(destination_id):
	"""DELETE: Remove a stored weather request record from the database."""
	destination = Destination.query.get(destination_id)
	if not destination:
		return jsonify({"error": "destination not found"}), 404

	db.session.delete(destination)
	db.session.commit()

	return jsonify({"message": "destination deleted", "id": destination_id}), 200

