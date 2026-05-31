"""Blueprint voor projecten en login-routes van de Overzichtspagina."""

from flask import Blueprint

bp = Blueprint("projects", __name__)

from app.Overzichtspagina import routes
from app.Overzichtspagina import loginroutes
