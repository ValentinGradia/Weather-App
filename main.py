from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from functools import partial

app = Flask(__name__)

#Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///destinations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import routes after app/db initialization to avoid circular import issues.
from app.routes import Weather
