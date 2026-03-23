from main import db

class Destination(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	weather = db.Column(db.String(100), nullable=False)
	description = db.Column(db.String(100), nullable=True)

	def to_dict(self):
		return {
			"id": self.id,
			"weather": self.weather,
			"description": self.description
		}

