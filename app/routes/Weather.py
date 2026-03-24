from datetime import datetime
import difflib
import json
from app.validation.Validation import UserInputDestinationValidation
from urllib.parse import urlencode
from urllib.request import urlopen

from flask import jsonify, request

from main import app, db
from app.models.Destination import Destination




def _read_json_response(url):
	"""Fetch and decode JSON payload from an HTTP endpoint."""
	with urlopen(url, timeout=10) as response:
		return json.loads(response.read().decode("utf-8"))



def _fetch_temperatures(latitude, longitude, start_date, end_date):
	"""Fetch daily min/max temperatures for a validated location and date range."""
	params = urlencode(
		{
			"latitude": latitude,
			"longitude": longitude,
			"start_date": start_date,
			"end_date": end_date,
			"daily": "temperature_2m_max,temperature_2m_min",
			"timezone": "auto",
		}
	)
	url = f"https://archive-api.open-meteo.com/v1/archive?{params}"
	data = _read_json_response(url)
	daily = data.get("daily", {})

	times = daily.get("time", [])
	max_values = daily.get("temperature_2m_max", [])
	min_values = daily.get("temperature_2m_min", [])

	temperatures = []
	for idx, day in enumerate(times):
		temperatures.append(
			{
				"date": day,
				"min_temperature": min_values[idx] if idx < len(min_values) else None,
				"max_temperature": max_values[idx] if idx < len(max_values) else None,
			}
		)

	return temperatures


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
@app.route("/destinations", methods=["POST"])
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
	
	return resolved_location

	# temperatures = _fetch_temperatures(
	# 	resolved_location["latitude"],
	# 	resolved_location["longitude"],
	# 	start.isoformat(),
	# 	end.isoformat(),
	# )

	# stored_payload = {
	# 	"location": {
	# 		"requested": location,
	# 		"resolved_name": resolved_location.get("name"),
	# 		"country": resolved_location.get("country"),
	# 		"latitude": resolved_location.get("latitude"),
	# 		"longitude": resolved_location.get("longitude"),
	# 	},
	# 	"date_range": {
	# 		"start_date": start.isoformat(),
	# 		"end_date": end.isoformat(),
	# 	},
	# 	"temperatures": temperatures,
	# }

	# destination = Destination(
	# 	weather=resolved_location.get("name", location),
	# 	description=json.dumps(stored_payload),
	# )
	# db.session.add(destination)
	# db.session.commit()

	# return jsonify(_destination_to_response(destination)), 201


@app.route("/destinations", methods=["GET"])
def get_destinations():
	"""READ: Return all stored weather requests from the database."""
	destinations = Destination.query.all()
	return jsonify([_destination_to_response(destination) for destination in destinations]), 200


@app.route("/destinations/<int:destination_id>", methods=["GET"])
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


@app.route("/destinations/<int:destination_id>", methods=["DELETE"])
def delete_destination(destination_id):
	"""DELETE: Remove a stored weather request record from the database."""
	destination = Destination.query.get(destination_id)
	if not destination:
		return jsonify({"error": "destination not found"}), 404

	db.session.delete(destination)
	db.session.commit()

	return jsonify({"message": "destination deleted", "id": destination_id}), 200


with app.app_context():
	# Ensure SQLite tables exist before handling CRUD requests.
	db.create_all()
