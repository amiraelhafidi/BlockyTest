"""Entry point for Flask application"""

import os
from flask import Flask
app/__init__.py

from dotenv import load_dotenv

app/__init__.py
from app.events import bp as events_bp
from app.main import bp as main_bp
from app.Overzichtspagina import bp as projects_bp


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["API_URL"] = os.getenv("API_URL")
    app.config["API_KEY"] = os.getenv("API_KEY")
    app.config["DATABASE"] = os.getenv("DATABASE")

    app.config.from_pyfile("settings.py")

    app.register_blueprint(main_bp)
app/__init__.py

    app.register_blueprint(projects_bp)

app/__init__.py
    app.register_blueprint(events_bp, url_prefix="/events")

    return app