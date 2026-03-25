import os
import tempfile
from main import create_app, db
import pytest
from Config import TestingConfig

#Fixture -> Functions that provide data or setup logic to our tests
@pytest.fixture
def app_context():
    app = create_app()
    app.config.from_object(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


