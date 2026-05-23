from flask import Blueprint

skills = Blueprint('skills', __name__)

from app.skills import routes