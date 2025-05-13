import logging
from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from flask_mail import Message
from . import db, mail
from .models import UserRole, Role

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
                rows = (
                    db.session
                    .query(Role.name)
                    .join(UserRole, Role.id == UserRole.role_id)
                    .filter(UserRole.user_id == user_id)
                    .all()
                )
                user_roles = {name for (name,) in rows}
                if not user_roles.intersection(required_roles):
                    return jsonify(error="Forbidden: insufficient role"), 403
            except Exception:
                logger.exception("Error verifying roles for user_id=%s", user_id)
                return jsonify(error="Unable to verify roles"), 500
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def send_email(to, subject, html_body):
    try:
        msg = Message(subject=subject, recipients=[to], html=html_body)
        msg.sender = current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@example.com")
        mail.send(msg)
    except Exception as e:
        logger.exception("Failed to send email to %s", to)
        raise
