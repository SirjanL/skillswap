from flask import Blueprint

requests_bp = Blueprint('requests_bp', __name__)

from app.requests import routes