from flask import Blueprint

matching = Blueprint('matching', __name__)

from app.matching import routes