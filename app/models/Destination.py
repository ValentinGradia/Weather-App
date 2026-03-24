from main import db

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

	def to_dict(self):
		return {
			"id": self.id,
			"location": self.location,
			"temperatures": [temperature.to_dict() for temperature in self.temperatures],
		}
	
	

