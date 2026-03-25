class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_weather.db"  #we create a new db to test our models
    TESTING = True