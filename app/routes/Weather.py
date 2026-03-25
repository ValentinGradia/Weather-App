import json
from app.models.Validation import UserInputDestinationValidation
from urllib.request import urlopen
from app.models.Temperature import Temperature
from datetime import datetime
import requests
from app.services.Youtube import get_video
from app.models.Exceptions import ValidationError
import json

from flask import Blueprint, jsonify, request, make_response

from main import db
from app.models.Destination import Destination


weather_bp = Blueprint("weather", __name__)


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
	lat,lon = Destination.get_lat_and_lng_through_coordinates(coordinates)

	location_formatted = resolved_location[0]['formatted']

	if Destination.already_exists(location_formatted.lower(), start_date, end_date):
		return jsonify({"error": "location already stored for this date range"}), 409
	
	temperatures_in_location_between_dates = []
	try:
		range_dates = UserInputDestinationValidation.get_all_dates_between(start_date, end_date)
	except ValidationError as exc:
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

	destinations = [d.to_dict() for d in Destination.query.all()]
	return destinations, 200


#READ: Return one stored weather request by its database ID.
@weather_bp.route("/destinations/<int:destination_id>", methods=["GET"])
def get_destination(destination_id):
	destination : Destination = Destination.query.get(destination_id)

	url_video_youtube = get_video(destination.location)
	if not destination:
		return jsonify({"error": "destination not found"}), 404

	response = destination.to_dict()
	response["youtube video"] = url_video_youtube
	return response, 200


#READ: Return one stored weather request by its locations
@weather_bp.route("/destinations/get_by_location", methods=["GET"])
def get_destination_through_location():
	data = request.get_json()
	location = data.get("location")

	try:
		resolved_location = UserInputDestinationValidation._handle_location(location)
	except Exception:
		return jsonify({"error": "failed to resolve location"}), 500
	
	url_video_youtube = get_video(resolved_location[0]["formatted"])

	destinations = [d.to_dict() for d in Destination.query.filter(db.func.lower(Destination.location) == resolved_location[0]["formatted"].lower()).all()]
	
	return {
		"destinations": destinations,
		"youtube video": url_video_youtube
	}, 200

##READ: Export a JSON of one stored weather request by its locations
@weather_bp.route("/destinations/export_by_location", methods=["GET"])
def export_destination_through_location():
	data = request.get_json()
	location = data.get("location")

	try:
		resolved_location = UserInputDestinationValidation._handle_location(location)
	except Exception:
		return jsonify({"error": "failed to resolve location"}), 500
	
	destination = Destination.query.filter(db.func.lower(Destination.location) == resolved_location[0]["formatted"].lower()).one()

	return export_json(destination), 200

##READ: Export a JSON of one stored weather request by its ID
@weather_bp.route("/destinations/export_by_id/<int:destination_id>", methods=["GET"])
def export_destination_through_id(destination_id):
	destination : Destination = Destination.query.get(destination_id)
	
	return export_json(destination), 200

#UPDATE: We update the destination by its ID
@weather_bp.route("/destinations/<int:destination_id>", methods=["PUT", "PATCH"])
def update_destination(destination_id):
	destination : Destination = Destination.query.get(destination_id)
	if not destination:
		return jsonify({"error": "destination not found"}), 404

	data = request.get_json()
	start_date = data.get("start_date")
	end_date = data.get("end_date")

	if not start_date or not end_date:
		return jsonify({"error": "start_date and end_date are required"}), 400

	try:
		start, end = UserInputDestinationValidation._validate_date_range(start_date, end_date)
	except ValidationError as exc:
		return jsonify({"error": str(exc)}), 400

	data_of_destination = UserInputDestinationValidation._handle_location(destination.location)
	coordinates = data_of_destination[0].get("geometry", {})

	lat,lon = Destination.get_lat_and_lng_through_coordinates(coordinates)

	range_dates = UserInputDestinationValidation.get_all_dates_between(start, end)

	#Get the temperatures of the specific location and delete these
	Temperature.query.filter_by(destination_id=destination_id).delete()

	for date in range_dates:
		temperature_response = Temperature.get_temperature(lat, lon, date)
		date_casted = datetime.strptime(date, "%Y-%m-%d").date()

		temperature = Temperature(destination.id, date_casted, temperature_response["morning"][:4], 
					temperature_response["afternoon"][:4], temperature_response["night"][:4])
		db.session.add(temperature)

	db.session.commit()

	return "The weather within the ranges of dates specified was updated correctly", 200

#DELETE: Remove a stored weather request record from the database
@weather_bp.route("/destinations/<int:destination_id>", methods=["DELETE"])
def delete_destination(destination_id):
	destination = Destination.query.get(destination_id)
	if not destination:
		return jsonify({"error": "destination not found"}), 404

	db.session.delete(destination)
	db.session.commit()

	return jsonify({"message": "destination deleted", "id": destination_id}), 200

#DELETE: Remove a stored weather request record from the database
@weather_bp.route("/destinations/delete_by_location", methods=["DELETE"])
def delete_destination_by_location():
	data = request.get_json()
	location = data.get("location")

	try:
		resolved_location = UserInputDestinationValidation._handle_location(location)
	except Exception:
		return jsonify({"error": "failed to resolve location"}), 500

	destination = Destination.query.filter(db.func.lower(Destination.location) == resolved_location[0]["formatted"].lower()).delete()
	
	db.session.delete(destination)
	db.session.commit()

	return jsonify({"message": "destination deleted"}), 200


def export_json(destination):
    response = make_response(json.dumps(destination.to_dict(), indent=2))
    response.headers["Content-Disposition"] = "attachment; filename=weather_data.json"
    response.headers["Content-Type"] = "application/json"
    return response


