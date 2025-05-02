import logging
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from flask_jwt_extended.utils import decode_token
from authlib.integrations.flask_client import OAuthError
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from . import db, bcrypt, oauth
from .models import User, RefreshToken, UserRole, Role, PasswordResetToken
from .utils import roles_required
logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=128))
    password = fields.Str(required=True, validate=validate.Length(min=8))
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
    access_token = create_access_token(identity=identity, expires_delta=access_expires)
    refresh_token = create_refresh_token(identity=identity, expires_delta=refresh_expires)
    jti = decode_token(refresh_token)["jti"]
    rt = RefreshToken(
        token=jti,
        user_id=user_id,
        expires_at=datetime.utcnow() + refresh_expires,
    )
    db.session.add(rt)
    db.session.commit()
    return access_token, refresh_token
@auth_bp.route("/register", methods=["POST"])
def register():
    data = RegisterSchema().load(request.get_json() or {})
    pw_hash = bcrypt.generate_password_hash(data["password"]).decode()
    user = User(email=data["email"], password_hash=pw_hash)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already registered."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Registration failed")
        return jsonify({"error": "Registration failed."}), 500
    access_token, refresh_token = _create_tokens(user.id)
    return (
        jsonify(
            message="Registration successful.",
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        201,
    )
@auth_bp.route("/login", methods=["POST"])
def login():
    data = LoginSchema().load(request.get_json() or {})
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.check_password_hash(
        user.password_hash, data["password"]
    ):
        return jsonify({"error": "Invalid credentials."}), 401
    access_token, refresh_token = _create_tokens(user.id)
    return (
        jsonify(
            message=f"Welcome back, {user.email}.",
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        200,
    )
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    jti = get_jwt()["jti"]
    rt = RefreshToken.query.filter_by(token=jti).first()
    if not rt or rt.revoked:
        return jsonify({"error": "Invalid refresh token."}), 401
    user_id = int(get_jwt_identity())
    access_token = create_access_token(
        identity=str(user_id),
        expires_delta=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    )
    return jsonify(access_token=access_token), 200
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required(refresh=True)
def logout():
    jti = get_jwt()["jti"]
    rt = RefreshToken.query.filter_by(token=jti).first()
    if rt:
        rt.revoked = True
        db.session.commit()
    return jsonify(message="Refresh token revoked."), 200
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found."}), 404
    return (
        jsonify(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        ),
        200,
    )
@auth_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    data = RequestPasswordResetSchema().load(request.get_json() or {})
    user = User.query.filter_by(email=data["email"]).first()
    if user:
        token = str(uuid.uuid4())
        expires = datetime.utcnow() + timedelta(hours=1)
        prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
        db.session.add(prt)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Failed to create reset token for %s", user.id)
    return (
        jsonify(message="If that email exists, you will receive reset instructions."),
        200,
    )
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = ResetPasswordSchema().load(request.get_json() or {})
    prt = PasswordResetToken.query.filter_by(token=data["token"], used=False).first()
    if not prt or prt.expires_at < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token."}), 400
    user = User.query.get(prt.user_id)
    user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode()
    prt.used = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to reset password for %s", user.id)
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
    except (OAuthError, KeyError):
        logger.exception("Google OAuth failed")
        return jsonify({"error": "Google login failed"}), 400
    email = userinfo.get("email")
    if not email:
        return jsonify({"error": "Google did not return an email"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        random_pw = uuid.uuid4().hex
        pw_hash = bcrypt.generate_password_hash(random_pw).decode()
        user = User(email=email, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
    access_token, refresh_token = _create_tokens(user.id)
    return (
        jsonify(
            message="Google login successful.",
            access_token=access_token,
            refresh_token=refresh_token,
        ),
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
        resp = oauth.github.get("user", token=token)
        profile = resp.json()
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
        random_pw = uuid.uuid4().hex
        pw_hash = bcrypt.generate_password_hash(random_pw).decode()
        user = User(email=email, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
    access_token, refresh_token = _create_tokens(user.id)
    return (
        jsonify(
            message="GitHub login successful.",
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        200,
    )
@auth_bp.route("/promote/<int:user_id>/<role_name>", methods=["POST"])
@jwt_required()
@roles_required("Admin")
def promote_user(user_id, role_name):
    user = User.query.get_or_404(user_id)
    role = Role.query.filter_by(name=role_name).first_or_404()
    if UserRole.query.filter_by(user_id=user.id, role_id=role.id).first():
        return jsonify({"error": "User already has that role."}), 409
    db.session.add(UserRole(user_id=user.id, role_id=role.id))
    db.session.commit()
    roles = [r.name for r in user.roles]
    return jsonify(message=f"{user.email} promoted to {role_name}", roles=roles), 200