import logging
from functools import wraps
from flask import jsonify, current_app, abort
from flask_jwt_extended import get_jwt_identity
from flask_mail import Message
from .extensions import db, mail
from .models import User, UserRole, Role

logger = logging.getLogger(__name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'pdf', 'mp4'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def roles_required(*required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                user_id = int(get_jwt_identity())
                user = db.session.get(User, user_id)
                if not user:
                    abort(404, description="User not found")
                user_role_names = [role.name for role in user.roles]
                if not any(role_name in user_role_names for role_name in required_roles):
                    current_app.logger.warning(
                        "Access denied: user %s with roles %s tried to access route requiring %s",
                        user_id, user_role_names, required_roles
                    )
                    return jsonify({"error": f"Forbidden: Requires one of {', '.join(required_roles)} roles"}), 403
                return fn(*args, **kwargs)
            except Exception as e:
                logger.exception("Error verifying roles for user_id=%s: %s", user_id, str(e))
                return jsonify({"error": "Unable to verify roles"}), 500
        return wrapper
    return decorator

def send_email(to, subject, html_body):
    try:
        msg = Message(subject=subject, recipients=[to], html=html_body)
        msg.sender = current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@example.com")
        mail.send(msg)
    except Exception as e:
        logger.exception("Failed to send email to %s: %s", to, str(e))
        raise