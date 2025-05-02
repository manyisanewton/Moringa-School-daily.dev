import logging
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import User, EmailVerificationToken
logger = logging.getLogger(__name__)
email_verification_bp = Blueprint("email_verification", __name__, url_prefix="/auth")
class RequestEmailSchema(Schema):
    email = fields.Email(required=True)
class ConfirmEmailSchema(Schema):
    token = fields.Str(required=True)
@email_verification_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(error=err.messages), 400
@email_verification_bp.route("/request-email-verification", methods=["POST"])
def request_verification():
    data = RequestEmailSchema().load(request.get_json() or {})
    user = User.query.filter_by(email=data["email"]).first_or_404()
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(days=1)
    evt = EmailVerificationToken(user_id=user.id, token=token, expires_at=expires)
    db.session.add(evt)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to create verification token for user %s", user.id)
        return jsonify(error="Could not create verification token"), 500
    return jsonify(message="Verification token created", token=token), 201
@email_verification_bp.route("/confirm-email", methods=["POST"])
def confirm_email():
    data = ConfirmEmailSchema().load(request.get_json() or {})
    evt = EmailVerificationToken.query.filter_by(token=data["token"]).first_or_404()
    if evt.used:
        return jsonify(error="Token already used"), 400
    if evt.expires_at < datetime.utcnow():
        return jsonify(error="Token expired"), 400
    evt.used = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to confirm email for token %s", evt.id)
        return jsonify(error="Could not confirm email"), 500
    return jsonify(message="Email verified"), 200