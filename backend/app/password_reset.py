import logging
import random
import re
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, current_app, url_for
from . import db, bcrypt, limiter
from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from sqlalchemy.exc import SQLAlchemyError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from .models import User, PhoneOTP, PasswordResetToken
from .utils import send_email
from twilio.rest import Client as TwilioClient

password_reset_bp = Blueprint("password_reset", __name__, url_prefix="/auth")

# --- Helpers ---
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

def get_twilio_client():
    try:
        return TwilioClient(
            current_app.config["TWILIO_ACCOUNT_SID"],
            current_app.config["TWILIO_AUTH_TOKEN"]
        )
    except TypeError:
        return TwilioClient()

def generate_reset_code():
    return f"{random.randint(0, 999999):06d}"

# --- Schemas ---
class RequestPasswordResetSchema(Schema):
    identifier = fields.Str(required=True)

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        idf = data["identifier"]
        if not (re.match(r"[^@]+@[^@]+\.[^@]+", idf) or re.match(r"^\+\d{10,15}$", idf)):
            raise ValidationError({"identifier": ["Must be a valid email or E.164 phone number."]})

RequestResetSchema = RequestPasswordResetSchema

class VerifyCodeSchema(Schema):
    email = fields.Str(required=True, validate=validate.Email())
    code = fields.Str(required=True, validate=validate.Length(equal=6))

class ResetPasswordSchema(Schema):
    code = fields.Str(required=True, validate=validate.Length(equal=6))
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get("new_password") != data.get("confirm_password"):
            raise ValidationError({"confirm_password": ["Passwords do not match"]})

# --- Error Handler ---
@password_reset_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(error=err.messages), 400

# --- SMS Reset Flow ---
@limiter.limit("5 per minute")
@password_reset_bp.route("/request-password-reset-sms", methods=["POST"])
def request_password_reset_sms():
    d = RequestPasswordResetSchema().load(request.get_json() or {})
    normalized = validate_phone(d["identifier"])
    if not normalized:
        return jsonify(error="Invalid phone number; must include a valid country code"), 400

    user = User.query.filter_by(phone_number=normalized).first()
    if not user or not user.is_active:
        return jsonify(message="If that account exists, reset instructions have been sent."), 200

    client = get_twilio_client()
    verify_sid = current_app.config.get("TWILIO_VERIFY_SERVICE_SID")
    use_verify = bool(verify_sid) and not current_app.testing

    if use_verify:
        try:
            client.verify.services(verify_sid).verifications.create(to=normalized, channel="sms")
        except Exception:
            use_verify = False

    if not use_verify:
        code = generate_reset_code()
        expires = datetime.utcnow() + timedelta(minutes=10)
        otp = PhoneOTP(phone_number=normalized, otp_code=code, expires_at=expires)
        db.session.add(otp)
        db.session.commit()

        client.messages.create(
            to=normalized,
            from_=current_app.config.get("TWILIO_FROM_NUMBER"),
            body=f"Your password reset code is {code}"
        )

    return jsonify(message="If that account exists, reset instructions have been sent."), 200

@limiter.limit("5 per minute")
@password_reset_bp.route("/reset-password-sms", methods=["POST"])
def reset_password_sms():
    d = ResetPasswordSchema().load(request.get_json() or {})
    normalized = validate_phone(d.get("phone_number", ""))
    if not normalized:
        return jsonify(error="Invalid phone number; must include a valid country code"), 400

    client = get_twilio_client()
    verify_sid = current_app.config.get("TWILIO_VERIFY_SERVICE_SID")
    use_verify = bool(verify_sid) and not current_app.testing

    if use_verify:
        try:
            check = client.verify.services(verify_sid).verification_checks.create(to=normalized, code=d["code"])
            if check.status != "approved":
                return jsonify(error="Invalid or expired code."), 400
        except Exception:
            use_verify = False

    if not use_verify:
        otp = (
            PhoneOTP.query
            .filter_by(phone_number=normalized, otp_code=d["code"])
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
        current_app.logger.exception("Failed to reset password for user %s", user.id)
        return jsonify(error="Could not reset password."), 500

    return jsonify(message="Password has been reset."), 200

# --- Email Reset Flow ---
@limiter.limit("5 per minute")
@password_reset_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset_email():
    from marshmallow import ValidationError as MV
    db.session.expire_all()
    try:
        data = RequestResetSchema().load(request.get_json() or {})
    except MV as err:
        return jsonify(error=err.messages), 400

    user = User.query.filter_by(email=data["identifier"]).first()
    if not user or not user.is_active:
        return jsonify(message="If that email exists, you will receive reset instructions."), 200

    code = generate_reset_code()
    expires = datetime.utcnow() + timedelta(hours=1)
    prt = PasswordResetToken(user_id=user.id, token=code, expires_at=expires)
    db.session.add(prt)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not create password reset token for user %s", user.id)
        return jsonify(error="Could not initiate password reset."), 500

    try:
        send_email(
            to=user.email,
            subject="Password Reset Code",
            html_body=f"Your password reset code is: <strong>{code}</strong>. Enter this code to reset your password."
        )
    except KeyError:
        current_app.logger.warning("MAIL_DEFAULT_SENDER not configured; skipping send_email")

    return jsonify(message="Password reset code sent."), 200

@limiter.limit("5 per minute")
@password_reset_bp.route("/verify-reset-code", methods=["POST"])
def verify_reset_code():
    from marshmallow import ValidationError as MV
    try:
        data = VerifyCodeSchema().load(request.get_json() or {})
    except MV as err:
        return jsonify(error=err.messages), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.is_active:
        return jsonify(error="Invalid email."), 400

    prt = PasswordResetToken.query.filter_by(
        user_id=user.id, token=data["code"], used=False
    ).first()
    if not prt or prt.expires_at < datetime.utcnow():
        return jsonify(error="Invalid or expired code."), 400

    return jsonify(message="Code verified."), 200

@limiter.limit("5 per minute")
@password_reset_bp.route("/reset-password", methods=["POST"])
def reset_password_email():
    from marshmallow import ValidationError as MV
    db.session.expire_all()
    try:
        data = ResetPasswordSchema().load(request.get_json() or {})
    except MV as err:
        return jsonify(error=err.messages), 400

    prt = PasswordResetToken.query.filter_by(token=data["code"], used=False).first()
    if not prt or prt.expires_at < datetime.utcnow():
        return jsonify(error="Invalid or expired code."), 400

    user = User.query.get(prt.user_id)
    if not user or not user.is_active:
        return jsonify(error="Invalid code."), 400

    user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode()
    prt.used = True

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to reset password for user %s", user.id)
        return jsonify(error="Could not reset password."), 500

    return jsonify(message="Password has been reset."), 200

# --- CLI for Cleanup ---
@password_reset_bp.cli.command("cleanup-expired-resets")
def cleanup_expired():
    now = datetime.utcnow()
    deleted_otp = PhoneOTP.query.filter(PhoneOTP.expires_at < now).delete()
    deleted_tokens = PasswordResetToken.query.filter(PasswordResetToken.expires_at < now, PasswordResetToken.used == False).delete()
    db.session.commit()
    print(f"Deleted {deleted_otp} OTPs and {deleted_tokens} reset tokens.")