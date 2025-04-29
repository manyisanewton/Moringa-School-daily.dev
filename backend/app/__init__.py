from flask import Flask
from app.extensions import db
from app.routes.notification_routes import notification_bp
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    
    return app
