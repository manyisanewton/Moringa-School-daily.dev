#  to be able to read from .env
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # create a secret key
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Google ids
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')