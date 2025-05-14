import logging
import warnings
import os
from sqlalchemy.exc import LegacyAPIWarning
from authlib.integrations.flask_client import OAuth
from flask import Flask, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session
from flask_mail import Mail
from twilio.rest import Client as TwilioClient
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import DevConfig, TestConfig
import requests
from flask import Blueprint, jsonify, request

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Suppress LegacyAPIWarning
warnings.filterwarnings("ignore", category=LegacyAPIWarning)
Flask._check_setup_finished = lambda self, f_name: None

# Initialize Flask extensions
db = SQLAlchemy(session_options={"expire_on_commit": False})
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
oauth = OAuth()
mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")
limiter = Limiter(key_func=get_remote_address)  # Initialize limiter

# Proxy Blueprint
proxy_bp = Blueprint("proxy", __name__, url_prefix="/proxy")

@proxy_bp.route("/youtube-videos", methods=["GET"])
def proxy_youtube_videos():
    RSS2JSON_API_KEY = "qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz"
    VIDEO_API = f"https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id=UC8butISFwT-Wl7EV0hUK0BQ&api_key={RSS2JSON_API_KEY}"
    try:
        response = requests.get(VIDEO_API)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        formatted_items = [
            {
                "guid": item["guid"],
                "title": item["title"],
                "link": item["link"],
                "pubDate": item["pubDate"],
            }
            for item in items
        ]
        return jsonify({"items": formatted_items}), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch YouTube videos: {str(e)}"}), 500

@proxy_bp.route("/devto-articles", methods=["GET"])
def proxy_devto_articles():
    ARTICLE_API = "https://dev.to/api/articles"
    try:
        response = requests.get(ARTICLE_API)
        response.raise_for_status()
        data = response.json()
        formatted_data = [
            {
                "id": article["id"],
                "title": article["title"],
                "url": article["url"],
                "published_at": article["published_at"],
            }
            for article in data
        ]
        return jsonify(formatted_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch Dev.to articles: {str(e)}"}), 500

@proxy_bp.route("/devto-article/<int:article_id>", methods=["GET"])
def proxy_devto_article(article_id):
    ARTICLE_DETAIL_API = f"https://dev.to/api/articles/{article_id}"
    try:
        response = requests.get(ARTICLE_DETAIL_API)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch Dev.to article: {str(e)}"}), 500

@proxy_bp.route("/devto-comments", methods=["GET"])
def proxy_devto_comments():
    article_id = request.args.get("a_id")
    if not article_id:
        return jsonify({"error": "Missing a_id parameter"}), 400
    COMMENTS_API = f"https://dev.to/api/comments?a_id={article_id}"
    try:
        response = requests.get(COMMENTS_API)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch Dev.to comments: {str(e)}"}), 500

@proxy_bp.route("/podcasts", methods=["GET"])
def proxy_podcasts():
    RSS2JSON_API_KEY = "qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz"
    AUDIO_API = f"https://api.rss2json.com/v1/api.json?rss_url=https://feeds.simplecast.com/4r7G7Z8a&api_key={RSS2JSON_API_KEY}"
    try:
        response = requests.get(AUDIO_API)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        formatted_items = [
            {
                "title": item["title"],
                "category": "Podcast",
                "date": item["pubDate"],
                "audio_url": item.get("enclosure", {}).get("url", ""),
            }
            for item in items
        ]
        return jsonify(formatted_items), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch podcasts: {str(e)}"}), 500

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    if isinstance(config_class, str) and config_class.lower() == "testing":
        app.config.from_object(TestConfig)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"check_same_thread": False}
        }
    else:
        app.config.from_object(config_class)

    # Configure upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'Uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize session
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    Session(app)

    # Enable CORS with correct origin and credentials
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",           # Local development
                "https://demo-cr4t.onrender.com"   # Production frontend
            ],
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        },
        r"/Uploads/*": {
            "origins": [
                "http://localhost:5173",
                "https://demo-cr4t.onrender.com"
            ],
            "methods": ["GET"],
            "supports_credentials": True
        }
    })

    # Initialize Flask extensions with app
    db.init_app(app)
    app.extensions["sqlalchemy"].db = db
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)  # Initialize limiter with app

    # Initialize Twilio client
    sid = app.config.get("TWILIO_ACCOUNT_SID")
    token = app.config.get("TWILIO_AUTH_TOKEN")
    if sid and token:
        app.twilio = TwilioClient(sid, token)
    else:
        app.twilio = None

    # Register OAuth providers
    oauth.register(
        name="github",
        client_id=app.config["GITHUB_CLIENT_ID"],
        client_secret=app.config["GITHUB_CLIENT_SECRET"],
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )
    
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        client_kwargs={"scope": "openid email profile"},
    )
    print("Google OAuth registered successfully")

    # Error handler for 404
    @app.errorhandler(404)
    def handle_not_found(error):
        message = error.description or "Not found"
        return jsonify({"error": message}), 404

    # Serve uploaded files
    @app.route('/Uploads/<filename>')
    def uploaded_file(filename):
        logger.info("Serving file: %s from %s", filename, app.config['UPLOAD_FOLDER'])
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Register proxy blueprint
    app.register_blueprint(proxy_bp)

    # Import and register blueprints at the END to avoid circular import issues
    from .admin import admin_bp
    from .audit import audit_bp
    from .auth import auth_bp
    from .categories import categories_bp
    from .comments import comments_bp
    from .content import content_bp
    from .email_verification import email_verification_bp
    from .notifications import notifications_bp
    from .password_reset import password_reset_bp
    from .profiles import profile_bp
    from .recommendations import recommendations_bp
    from .reactions import reactions_bp
    from .subscriptions import subscriptions_bp
    from .users import user_bp
    from .wishlists import wishlists_bp

    blueprints = [
        admin_bp,
        audit_bp,
        auth_bp,
        categories_bp,
        comments_bp,
        content_bp,
        email_verification_bp,
        notifications_bp,
        password_reset_bp,
        profile_bp,
        recommendations_bp,
        reactions_bp,
        subscriptions_bp,
        user_bp,
        wishlists_bp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)

    return app, socketio