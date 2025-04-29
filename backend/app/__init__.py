from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.routes.notification_routes import notification_bp
from flask_socketio import SocketIO, join_room, leave_room
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_class=Config):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    # Initialize CORS
    CORS(app)
    app.secret_key = app.config['SECRET_KEY']
    app.config['SESSION_COOKIE'] = '5RDCVGT7UJMKOL'

    # Register blueprints
    from .auth_routes import auth_bp, init_oauth
    from .users.routes import users_bp
   
    

    # Initialize OAuth
    init_oauth(app)

    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
  

    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        pass  # Connection handled by JWT in routes

    @socketio.on('join')
    def on_join(data):
        user_id = data['user_id']
        join_room(user_id)

    @socketio.on('leave')
    def on_leave(data):
        user_id = data['user_id']
        leave_room(user_id)

    return app