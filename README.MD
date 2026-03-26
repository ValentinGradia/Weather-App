# Weather App API

## Project Description
This project is a Flask REST API that lets users request weather forecasts for a destination and date range, then stores those requests in a SQLite database.

The app:
- Validates user input (location and date range).
- Resolves the location to coordinates using OpenCage.
- Fetches weather forecast data from OpenWeather.
- Stores destinations and temperatures in a relational database using SQLAlchemy.
- Offers CRUD endpoints for weather records.
- Adds a related YouTube video link for destination-based queries.

## What I Built
I developed a backend weather service with:
- Flask application factory setup and app initialization.
- SQLAlchemy models with one-to-many relationship:
  - Destination has many Temperature records.
- Input/date validation with custom validation exceptions.
- Integration with three external services:
  - OpenCage (geocoding)
  - OpenWeather (forecast)
  - YouTube Data API (related destination video)
- Database migration support via Flask-Migrate/Alembic.
- Unit tests for core model behavior (destination storage, duplicate detection, model links).

## Important API Limitation (OpenWeather)
This project uses the OpenWeather 5-day/3-hour forecast endpoint (not the paid long-range API).

That means:
- Forecast data is only available for approximately the next 5 days.
- Requests for dates beyond this range may not return usable data.
- The free OpenWeather plan does not include extended forecast beyond that limit.

This limitation is from OpenWeather pricing/plan restrictions, not from the application logic.

## Tech Stack
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Alembic
- Requests
- OpenCage Geocoder
- OpenWeather
- SQLite
- Pytest

## Project Structure
- main.py: Flask app factory, DB initialization, CLI command.
- app/models: database models, validators, custom exceptions.
- app/routes: API endpoints (CRUD + export).
- app/services: external API integration helpers.
- Configuration: environment-specific config.
- migrations: Alembic migration scripts.
- tests: unit tests.

## Setup and Run

1. Create and activate a virtual environment 

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Run the API:
```powershell
python main.py
```

The app starts in debug mode by default.

## Database
This project uses SQLite.
Development DB is configured in Configuration/Config.py as destinations.db.

To initialize tables from the Flask CLI command:
```powershell
flask --app main init-db
```

You can also use Flask-Migrate/Alembic workflow if needed.

## Endpoints
- POST /destinations
  - Create a destination weather request with location, start_date, end_date.

- GET /destinations
  - Return all stored destination weather requests.

- GET /destinations/<destination_id>
  - Return one request by id, including a related YouTube link.

- GET /destinations/get_by_location
  - Return stored requests by location (normalized through geocoding).

- GET /destinations/export_by_location
  - Export stored location data as JSON download.

- GET /destinations/export_by_id/<destination_id>
  - Export one stored record by id as JSON download.

- PUT/PATCH /destinations/<destination_id>
  - Update date range and recalculate temperatures.

- DELETE /destinations/<destination_id>
  - Delete one record by id.

- DELETE /destinations/delete_by_location
  - Delete record(s) by location.

## Testing
Unit tests are available for model behavior.

Run:
```powershell
python -m pytest tests/unit/test_models.py
```

