from datetime import date

import pytest
from main import db
from app.models.Destination import Destination
from app.models.Temperature import Temperature


#Pytest injects the app_context automatically.

def test_destination_stores_submitted_location(app_context):
    destination = Destination("Paris, France")

    db.session.add(destination)
    db.session.commit()

    saved_destination = Destination.query.first()

    assert saved_destination is not None
    assert saved_destination.location == "Paris, France"


def test_already_exists_returns_true_for_same_location_and_exact_date_range(app_context):
    destination = Destination("Paris, France")
    db.session.add(destination)
    db.session.flush()

    db.session.add_all(
        [
            Temperature(destination.id, date(2026, 3, 1), 10.0, 15.0, 8.0),
            Temperature(destination.id, date(2026, 3, 2), 11.0, 16.0, 9.0),
            Temperature(destination.id, date(2026, 3, 3), 9.0, 14.0, 7.0),
        ]
    )
    db.session.commit()

    assert Destination.already_exists("paris, france", "2026-03-01", "2026-03-03") is True


def test_already_exists_returns_false_for_wrong_location(app_context):
    destination = Destination("Paris, France")
    db.session.add(destination)
    db.session.flush()

    db.session.add_all(
        [
            Temperature(destination.id, date(2026, 3, 1), 10.0, 15.0, 8.0),
            Temperature(destination.id, date(2026, 3, 2), 11.0, 16.0, 9.0),
        ]
    )
    db.session.commit()

    assert Destination.already_exists("london, uk", "2026-03-01", "2026-03-02") is False


def test_already_exists_returns_false_for_different_date_range(app_context):
    destination = Destination("Paris, France")
    db.session.add(destination)
    db.session.flush()

    db.session.add_all(
        [
            Temperature(destination.id, date(2026, 3, 1), 10.0, 15.0, 8.0),
            Temperature(destination.id, date(2026, 3, 2), 11.0, 16.0, 9.0),
        ]
    )
    db.session.commit()

    assert Destination.already_exists("paris, france", "2026-03-01", "2026-03-03") is False


def test_temperature_is_linked_to_correct_destination(app_context):
    paris = Destination("Paris, France")
    london = Destination("London, UK")
    db.session.add_all([paris, london])
    db.session.flush()

    db.session.add(Temperature(paris.id, date(2026, 3, 1), 12.0, 18.0, 9.0))
    db.session.add(Temperature(london.id, date(2026, 3, 1), 7.0, 10.0, 5.0))
    db.session.commit()

    paris_temps = Temperature.query.filter_by(destination_id=paris.id).all()
    london_temps = Temperature.query.filter_by(destination_id=london.id).all()

    assert len(paris_temps) == 1
    assert len(london_temps) == 1
    assert paris_temps[0].destination.location == "Paris, France"
    assert london_temps[0].destination.location == "London, UK"