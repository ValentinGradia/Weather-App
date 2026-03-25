from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import click
import os
from flask_migrate import Migrate
from Configuration.Config import DevelopmentConfig


db = SQLAlchemy()


def create_app(config=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)

    # Configure the path to SQLite database
    app.config.from_object(config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    #Initiate the migration
    Migrate(app, db)

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
