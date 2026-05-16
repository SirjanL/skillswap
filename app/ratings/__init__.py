from flask import Blueprint

ratings = Blueprint('ratings', __name__)

from app.ratings import routes