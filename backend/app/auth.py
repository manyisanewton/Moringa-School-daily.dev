import logging
import uuid
import random
from datetime import datetime, timedelta
from marshmallow import Schema, fields, validate, ValidationError, validates_schema, pre_load
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import(
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from flask_jwt_extended.utils import decode_token
from authlib.integrations.flask_client import OAuthError
from sqlalchemy.exc import SQLAlchemyError
from twilio.rest import Client as TwilioClient
from . import db, bcrypt, oauth, mail
from .models import(
    User,
    RefreshToken,
    PasswordResetToken,
    Role,
    UserRole,
    UserRoleEnum,
)
from .utils import roles_required, send_email
logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(max=128))
    email = fields.Email(required=True, validate=validate.Length(max=128))
    password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(
        required=True, validate=validate.Length(min=8), load_only=True
    )
    role = fields.Str(
        load_default=UserRoleEnum.USER.value,
        validate=validate.OneOf([r.value for r in UserRoleEnum]),
    )
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data["password"] != data["confirm_password"]:
            raise ValidationError({"confirm_password": ["Passwords must match."]})
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
class RequestPasswordResetSchema(Schema):
    email = fields.Email(required=True)
class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
@auth_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify({"error": err.messages}), 400
def _create_tokens(user_id: int):
    access_expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    refresh_expires = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    identity = str(user_id)
    at = create_access_token(identity=identity, expires_delta=access_expires)
    rt = create_refresh_token(identity=identity, expires_delta=refresh_expires)
    jti = decode_token(rt)["jti"]
    expires_at = datetime.utcnow() + refresh_expires
    db.session.add(RefreshToken(token=jti, user_id=user_id, expires_at=expires_at))
    db.session.commit()
    return at, rt
@auth_bp.route("/register", methods=["POST"])
def register():
    raw_data = request.get_json() or {}
    if "password" in raw_data and "confirm_password" not in raw_data and "role" not in raw_data:
        raw_data["confirm_password"] = raw_data["password"]
    data = RegisterSchema().load(raw_data)
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered."}), 409
    role_name = data["role"]
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name, description=role_name)
        db.session.add(role)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
    pw_hash = bcrypt.generate_password_hash(data["password"]).decode()
    user = User(email=data["email"], name=data["name"], password_hash=pw_hash)
    db.session.add(user)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Registration failed")
        return jsonify({"error": "Registration failed."}), 500
    try:
        db.session.add(UserRole(user_id=user.id, role_id=role.id))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Role assignment failed for user %s", user.id)
        return jsonify({"error": "Could not assign role."}), 500
    at, rt = _create_tokens(user.id)
    return(
        jsonify(
            message="Registration successful.",
            access_token=at,
            refresh_token=rt,
            roles=[role_name],
        ),
        201,
    )
@auth_bp.route("/login", methods=["POST"])
def login():
    data = LoginSchema().load(request.get_json() or {})
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials."}), 401
    at, rt = _create_tokens(user.id)
    return(
        jsonify(
            message="Welcome back!",
            access_token=at,
            refresh_token=rt,
            roles=[r.name for r in user.roles],
        ),
        200,
    )
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    jti = get_jwt()["jti"]
    token = RefreshToken.query.filter_by(token=jti, revoked=False).first()
    if not token:
        return jsonify({"error": "Token revoked."}), 401
    new_at = create_access_token(identity=get_jwt_identity())
    return jsonify(access_token=new_at), 200
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required(refresh=True)
def logout():
    jti = get_jwt()["jti"]
    token = RefreshToken.query.filter_by(token=jti, revoked=False).first()
    if token:
        token.revoked = True
        db.session.commit()
    return jsonify(message="Logged out."), 200
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return(
        jsonify(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            roles=[r.name for r in user.roles],
        ),
        200,
    )
@auth_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    from .models import PasswordResetToken
    db.session.expire_all()
    data = RequestPasswordResetSchema().load(request.get_json() or {})
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.is_active:
        return(
            jsonify(
                message="You will receive reset instructions shortly!"
            ),
            200,
        )
    token = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(hours=1)
    prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expiry)
    db.session.add(prt)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Could not create password reset token for user %s", user.id)
        return jsonify({"error": "Could not initiate password reset."}), 500
    reset_url = url_for("auth.reset_password", _external=True) + f"?token={token}"
    try:
        send_email(
            to=user.email,
            subject="Password Reset",
            html_body=f"Click here to reset your password: {reset_url}",
        )
    except KeyError:
        logger.warning("MAIL_DEFAULT_SENDER not configured; skipping send_email")
    return jsonify(message="Password reset email sent."), 200
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    from .models import PasswordResetToken
    db.session.expire_all()
    data = ResetPasswordSchema().load(request.get_json() or {})
    prt = PasswordResetToken.query.filter_by(token=data["token"], used=False).first()
    if not prt or prt.expires_at < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token."}), 400
    user = User.query.get(prt.user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Invalid token."}), 400
    user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode()
    prt.used = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to reset password for user %s", user.id)
        return jsonify({"error": "Could not reset password."}), 500
    return jsonify(message="Password has been reset."), 200
@auth_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.callback_google", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
@auth_bp.route("/callback/google")
def callback_google():
    try:
        token = oauth.google.authorize_access_token()
        userinfo = oauth.google.parse_id_token(token)
    except OAuthError:
        logger.exception("Google OAuth failed")
        return jsonify({"error": "Google login failed"}), 400
    email = userinfo.get("email")
    if not email:
        return jsonify({"error": "Google did not return an email"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        rand_pw = uuid.uuid4().hex
        pw_hash = bcrypt.generate_password_hash(rand_pw).decode()
        user = User(email=email, name=userinfo.get("name", ""), password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
    at, rt = _create_tokens(user.id)
    return(
        jsonify(message="Google login successful.", access_token=at, refresh_token=rt),
        200,
    )
@auth_bp.route("/login/github")
def login_github():
    redirect_uri = url_for("auth.callback_github", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)
@auth_bp.route("/callback/github")
def callback_github():
    try:
        token = oauth.github.authorize_access_token()
        profile = oauth.github.get("user", token=token).json()
        email = profile.get("email") or next(
            e["email"]
            for e in oauth.github.get("user/emails", token=token).json()
            if e.get("primary")
        )
    except Exception:
        logger.exception("GitHub OAuth failed")
        return jsonify({"error": "GitHub login failed"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        rand_pw = uuid.uuid4().hex
        pw_hash = bcrypt.generate_password_hash(rand_pw).decode()
        user = User(email=email, name=profile.get("name", ""), password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
    at, rt = _create_tokens(user.id)
    return(
        jsonify(message="GitHub login successful.", access_token=at, refresh_token=rt),
        200,
    )
@auth_bp.route("/promote/<int:user_id>/<role_name>", methods=["POST"])
@jwt_required()
@roles_required("Admin")
def promote_user(user_id, role_name):
    user = User.query.get(user_id)
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({"error": "Role not found."}), 404
    if UserRole.query.filter_by(user_id=user.id, role_id=role.id).first():
        return jsonify({"error": "User already has that role."}), 409
    db.session.add(UserRole(user_id=user.id, role_id=role.id))
    db.session.commit()
    return(
        jsonify(
            message=f"{user.email} promoted to {role_name}",
            roles=[r.name for r in user.roles],
        ),
        200,
    )