from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

# necessary extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)

    # load configuration
    app.config.from_object(config_class)

    # initializing extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # initialize CORS
    CORS(app)
    app.secret_key = app.config['SECRET_KEY']
    app.config['SESSION_COOKIE'] = '5RDCVGT7UJMKOL'

    # register blueprints
    from .auth_routes import auth_bp, init_oauth
    
    init_oauth(app)
    app.register_blueprint(auth_bp)

    return app
