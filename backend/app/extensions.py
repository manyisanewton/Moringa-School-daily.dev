import logging
from sqlalchemy.exc import LegacyAPIWarning
import warnings
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Suppress LegacyAPIWarning
warnings.filterwarnings("ignore", category=LegacyAPIWarning)

# Initialize Flask extensions
db = SQLAlchemy(session_options={"expire_on_commit": False})
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
oauth = OAuth()
mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    storage_options={"socket_connect_timeout": 5},
    default_limits=["200 per day", "50 per hour"],
    strategy="fixed-window"
)
session = Session()