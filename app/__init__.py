from flask import Flask
from config import DevConfig

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    return app
