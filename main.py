from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import app.routes.Weather
from functools import partial
from geopy.geocoders import Nominatim

app = Flask(__name__)
geolocator = Nominatim(user_agent=__name__)
geocode = partial(geolocator.geocode, language="es")

#Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///destinations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import routes so endpoint decorators are registered on app startup.