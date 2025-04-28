#  to be able to read from .env
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # create a secret key
    SECRET_KEY = os.getenv('SECRET_KEY', 'secretkey')