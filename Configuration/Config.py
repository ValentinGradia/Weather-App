class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_weather.db"  #we create a new db to test our models
    TESTING = True


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///destinations.db" 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev"