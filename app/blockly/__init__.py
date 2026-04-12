from flask import Blueprint
bp = Blueprint("blockly", __name__)
from app.blockly import routes
