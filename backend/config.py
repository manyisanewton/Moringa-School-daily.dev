import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost/moringa_project')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
