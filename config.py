import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this-later'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:8079@localhost/skillswap_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False