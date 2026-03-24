from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import click
import os


db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.py', silent=True)
    app.config.from_mapping(SECRET_KEY='dev')

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configure the path to SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///destinations.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    db.init_app(app)

    from app.routes.Weather import weather_bp

    app.register_blueprint(weather_bp)

    @click.command("init-db")
    def init_db_command():
        """Command for initializing the database."""
        with app.app_context():
            db.create_all()

    app.cli.add_command(init_db_command)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
