import requests #import request to call externals apis 
from datetime import datetime
from statistics import mean
from main import db

class Temperature(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	destination_id = db.Column(db.Integer, db.ForeignKey("destination.id"), nullable=False)
	date = db.Column(db.Date, nullable=False)
	temperature_morning = db.Column(db.Float, nullable=False)
	temperature_afternoon = db.Column(db.Float, nullable=False)
	temperature_night = db.Column(db.Float, nullable=False)

	#We link our tables
	destination = db.relationship("Destination", back_populates="temperatures")

	def __init__(
		self,
		destination_id,
		date,
		temperature_morning,
		temperature_afternoon,
		temperature_night,
	):
		self.destination_id = destination_id
		self.date = date
		self.temperature_morning = temperature_morning
		self.temperature_afternoon = temperature_afternoon
		self.temperature_night = temperature_night

	def to_dict(self):
		return {
			"id": self.id,
			"destination_id": self.destination_id,
			"date": self.date.isoformat() if self.date else None,
			"temperature_morning": self.temperature_morning,
			"temperature_afternoon": self.temperature_afternoon,
			"temperature_night": self.temperature_night,
		}
	
	@staticmethod
	def get_temperature(lat, lon, date):
		url = "https://api.openweathermap.org/data/2.5/forecast"
		api_key = "13b6c0efee30c5b09271adb991c804cf"


		params = {
			"lat": lat,
			"lon": lon,
			"appid": api_key,
			"units": "metric"
		}

		response = requests.get(url, params=params)
		response.raise_for_status() #if request failed, raise an error

		data = response.json()

		# Filter by date
		target_date = datetime.strptime(date, "%Y-%m-%d").date()
		filtered = [
			entry for entry in data["list"]
			if datetime.fromtimestamp(entry["dt"]).date() == target_date
		]

		# Group by time of day
		result = Temperature.group_by_time_of_day(filtered)
		return result
	
	@staticmethod
	def group_by_time_of_day(entries):
		morning = []    # 06:00 - 11:00
		afternoon = []  # 12:00 - 17:00
		night = []      # 18:00 - 23:00 and 00:00 - 05:00

		for entry in entries:
			hour = datetime.fromtimestamp(entry["dt"]).hour
			temp = entry["main"]["temp"]

			if 6 <= hour < 12:
				morning.append(temp)
			elif 12 <= hour < 18:
				afternoon.append(temp)
			else:
				night.append(temp)

		#mean -> average
		return {
			"morning": f"{mean(morning):.2f} °C",
			"afternoon": f"{mean(afternoon):.2f} °C",
			"night": f"{mean(night):.2f} °C"
		}