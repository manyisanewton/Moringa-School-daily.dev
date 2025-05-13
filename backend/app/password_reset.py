import logging
import uuid
import random
import re
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, url_for
from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from sqlalchemy.exc import SQLAlchemyError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from . import db, bcrypt
from .models import User, PhoneOTP, PasswordResetToken
from .utils import send_email
from twilio.rest import Client as TwilioClient
logger = logging.getLogger(__name__)
password_reset_bp = Blueprint("password_reset", __name__, url_prefix="/auth")
def validate_phone(number: str):
    if re.match(r"^\+\d{10,15}$", number):
        return number
    try:
        parsed = phonenumbers.parse(number, None)
    except NumberParseException:
        return None
    if not phonenumbers.is_valid_number(parsed):
        return None
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
class RequestPasswordResetSchema(Schema):
    identifier = fields.Str(required=True)
    @validates_schema
    def validate_identifier(self, data, **kwargs):
        idf = data["identifier"]
        email_re = r"[^@]+@[^@]+\.[^@]+"
        phone_re = r"^\+\d{10,15}$"
        if not (re.match(email_re, idf) or re.match(phone_re, idf)):
            raise ValidationError(
                {"identifier": ["Must be a valid email or E.164 phone number."]}
            )
RequestResetSchema = RequestPasswordResetSchema
class ResetPasswordSchema(Schema):
    token = fields.Str(load_default=None)
    phone_number = fields.Str(load_default=None)
    otp_code = fields.Str(load_default=None, validate=validate.Length(equal=6))
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(load_default=None)
    @validates_schema
    def require_one(self, data, **kwargs):
        if not data.get("token") and not (
            data.get("phone_number") and data.get("otp_code")
        ):
            raise ValidationError(
                "Must provide either 'token' (email flow) or both 'phone_number' and 'otp_code' (SMS flow)."
            )
        if data.get("new_password") and data.get("confirm_password") is None:
            raise ValidationError({"confirm_password": ["Missing data for confirm_password"]})
        if data.get("new_password") != data.get("confirm_password"):
            raise ValidationError({"confirm_password": ["Passwords do not match"]})
@password_reset_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(error=err.messages), 400
@password_reset_bp.route("/request-password-reset-sms", methods=["POST"])
def request_password_reset_sms():
    d = RequestPasswordResetSchema().load(request.get_json() or {})
    normalized = validate_phone(d["identifier"])
    if not normalized:
        return jsonify(error="Invalid phone number; must include a valid country code"), 400
    user = User.query.filter_by(phone_number=normalized).first()
    if not user or not user.is_active:
        return jsonify(message="If that account exists, reset instructions have been sent."), 200
    try:
        client = TwilioClient(
            current_app.config["TWILIO_ACCOUNT_SID"],
            current_app.config["TWILIO_AUTH_TOKEN"]
        )
    except TypeError:
        client = TwilioClient()
    verify_sid = current_app.config.get("TWILIO_VERIFY_SERVICE_SID")
    use_verify = bool(verify_sid)
    if use_verify:
        try:
            client.verify.services(verify_sid).verifications.create(
                to=normalized, channel="sms"
            )
        except Exception:
            use_verify = False
    if not use_verify:
        code = f"{random.randint(0, 999999):06d}"
        expires = datetime.utcnow() + timedelta(minutes=10)
        otp = PhoneOTP(phone_number=normalized, otp_code=code, expires_at=expires)
        db.session.add(otp)
        db.session.commit()
        try:
            client.messages.create(
                to=normalized,
                from_=current_app.config.get("TWILIO_FROM_NUMBER"),
                body=f"Your password reset code is {code}"
            )
        except AttributeError:
            logger.warning("Twilio client has no .messages; skipping SMS")
    return jsonify(message="If that account exists, reset instructions have been sent."), 200
@password_reset_bp.route("/reset-password-sms", methods=["POST"])
def reset_password_sms():
    d = ResetPasswordSchema().load(request.get_json() or {})
    normalized = validate_phone(d.get("phone_number", ""))
    if not normalized:
        return jsonify(error="Invalid phone number; must include a valid country code"), 400
    try:
        client = TwilioClient(
            current_app.config["TWILIO_ACCOUNT_SID"],
            current_app.config["TWILIO_AUTH_TOKEN"]
        )
    except TypeError:
        client = TwilioClient()
    verify_sid = current_app.config.get("TWILIO_VERIFY_SERVICE_SID")
    use_verify = bool(verify_sid)
    if use_verify:
        try:
            check = client.verify.services(verify_sid).verification_checks.create(
                to=normalized, code=d["otp_code"]
            )
            if check.status != "approved":
                return jsonify(error="Invalid or expired code."), 400
        except Exception:
            use_verify = False
    if not use_verify:
        otp = (
            PhoneOTP.query
            .filter_by(phone_number=normalized, otp_code=d["otp_code"])
            .filter(PhoneOTP.expires_at > datetime.utcnow())
            .order_by(PhoneOTP.created_at.desc())
            .first()
        )
        if not otp:
            return jsonify(error="Invalid or expired code."), 400
        db.session.delete(otp)
        db.session.commit()
    user = User.query.filter_by(phone_number=normalized).first()
    if not user or not user.is_active:
        return jsonify(error="Invalid request."), 400
    user.password_hash = bcrypt.generate_password_hash(d["new_password"]).decode()
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to reset password for user %s", user.id)
        return jsonify(error="Could not reset password."), 500
    return jsonify(message="Password has been reset."), 200
@password_reset_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset_email():
    from .models import PasswordResetToken
    db.session.expire_all()
    from marshmallow import ValidationError as MV
    try:
        data = RequestResetSchema().load(request.get_json() or {})
    except MV as err:
        return jsonify(error=err.messages), 400
    user = User.query.filter_by(email=data["identifier"]).first()
    if not user or not user.is_active:
        return jsonify(message="If that email exists, you will receive reset instructions."), 200
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=1)
    prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
    db.session.add(prt)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Could not create password reset token for user %s", user.id)
        return jsonify(error="Could not initiate password reset."), 500
    reset_url = url_for("password_reset.reset_password_email", _external=True) + f"?token={token}"
    try:
        send_email(
            to=user.email,
            subject="Password Reset",
            html_body=f"Click here to reset your password: {reset_url}"
        )
    except KeyError:
        logger.warning("MAIL_DEFAULT_SENDER not configured; skipping send_email")
    return jsonify(message="Password reset email sent."), 200
@password_reset_bp.route("/reset-password", methods=["POST"])
def reset_password_email():
    from .models import PasswordResetToken
    db.session.expire_all()
    from marshmallow import ValidationError as MV
    try:
        data = ResetPasswordSchema().load(request.get_json() or {})
    except MV as err:
        return jsonify(error=err.messages), 400
    prt = PasswordResetToken.query.filter_by(token=data["token"], used=False).first()
    if not prt or prt.expires_at < datetime.utcnow():
        return jsonify(error="Invalid or expired token."), 400
    user = User.query.get(prt.user_id)
    if not user or not user.is_active:
        return jsonify(error="Invalid token."), 400
    user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode()
    prt.used = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to reset password for user %s", user.id)
        return jsonify(error="Could not reset password."), 500
    return jsonify(message="Password has been reset."), 200