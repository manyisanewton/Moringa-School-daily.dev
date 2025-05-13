import warnings
from sqlalchemy.exc import LegacyAPIWarning
from authlib.integrations.flask_client import OAuth
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from twilio.rest import Client as TwilioClient
from backend.config import DevConfig, TestConfig
warnings.filterwarnings("ignore", category=LegacyAPIWarning)
Flask._check_setup_finished = lambda self, f_name: None
db = SQLAlchemy(session_options={"expire_on_commit": False})
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
oauth = OAuth()
mail = Mail()
def create_app(config_name=DevConfig):
    app = Flask(__name__)
    if isinstance(config_name, str) and config_name.lower() == "testing":
        app.config.from_object(TestConfig)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"check_same_thread": False}
        }
    else:
        app.config.from_object(config_name)
    db.init_app(app)
    app.extensions["sqlalchemy"].db = db
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)
    sid = app.config.get("TWILIO_ACCOUNT_SID")
    token = app.config.get("TWILIO_AUTH_TOKEN")
    if sid and token:
        app.twilio = TwilioClient(sid, token)
    else:
        app.twilio = None
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
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        client_kwargs={"scope": "openid email profile"},
    )
    @app.errorhandler(404)
    def handle_not_found(error):
        message = error.description or "Not found"
        return jsonify({"error": message}), 404
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
    for bp in (
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
    ):
        app.register_blueprint(bp)
    return app