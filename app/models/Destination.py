from main import db
from app.models.Validation import UserInputDestinationValidation
from datetime import datetime

class Destination(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	location = db.Column(db.String(100), nullable=False)

	#One destination might has many temperatures -> This is pyhton link between tables through ORM, not a value stored
	temperatures = db.relationship(
		"Temperature",
		back_populates="destination",
		cascade="all, delete-orphan",
	)

	def __init__(self, location):
		self.location = location

	#Return True when the given location already exists in database.
	@staticmethod
	def already_exists(location, start_date, end_date):
		flag = False

		normalized_location = location.strip().lower()
		dates_between_params = UserInputDestinationValidation.get_all_dates_between(start_date, end_date)

		stored_locations = [d.to_dict() for d in Destination.query.filter(db.func.lower(Destination.location) == normalized_location).all()]

		if(len(stored_locations) > 1):
			for locations in stored_locations:
				dates = [temp["date"] for item in locations for temp in item["temperatures"]]
				if(dates_between_params == dates):
					flag = True
		else:
			dates = [temp["date"] for item in stored_locations for temp in item["temperatures"]]
			if(dates_between_params == dates):
				flag = True
		return flag
		
	def to_dict(self):
		return {
			"id": self.id,
			"location": self.location,
			"temperatures": [temperature.to_dict() for temperature in self.temperatures],
		}
	
	

