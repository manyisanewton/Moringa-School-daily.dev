import logging
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, url_for, redirect, session
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
from .extensions import db, bcrypt, oauth, limiter  # Added limiter import
from .models import User, RefreshToken, PasswordResetToken, Role, UserRole
from .permissions import requires_role

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(max=128))
    email = fields.Email(required=True, validate=validate.Length(max=128))
    phone = fields.Str(required=False, validate=validate.Length(max=15))
    role = fields.Str(required=True, validate=validate.OneOf(["Admin", "TechWriter", "User"]))
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
    access_token = create_access_token(
        identity=identity,
        expires_delta=access_expires,
    )
    refresh_token = create_refresh_token(
        identity=identity,
        expires_delta=refresh_expires,
    )
    jti = decode_token(refresh_token)["jti"]
    expires_at = datetime.utcnow() + refresh_expires
    rt = RefreshToken(
        token=jti,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.session.add(rt)
    db.session.commit()
    return access_token, refresh_token

@auth_bp.route("/register", methods=["POST"])
def register():
    d = RegisterSchema().load(request.get_json() or {})
    h = bcrypt.generate_password_hash(d["password"]).decode()
    existing_user = User.query.filter_by(email=d["email"]).first()
    if existing_user:
        return jsonify({
            "error": "Email already registered. Please log in or use a different email.",
            "suggestion": "login"
        }), 409

    u = User(email=d["email"], name=d["name"], password_hash=h)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if isinstance(getattr(e, "orig", None), str):
            logger.exception("Registration failed")
            return jsonify({"error": "Registration failed."}), 500
        return jsonify({"error": "Email already registered."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Registration failed")
        return jsonify({"error": "Registration failed."}), 500

    role_name = d["role"]
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        db.session.rollback()
        return jsonify({"error": f"Role {role_name} not found."}), 400
    user_role = UserRole(user_id=u.id, role_id=role.id)
    db.session.add(user_role)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to assign role to user %s", u.id)
        return jsonify({"error": "Failed to assign role."}), 500

    at, rtok = _create_tokens(u.id)
    logger.info("User %s registered with role %s", d["email"], role_name)
    return (
        jsonify(
            message="Registration successful.",
            access_token=at,
            refresh_token=rtok,
            role=role_name,
            redirect_url=f"/{role_name.lower()}dashboard"
        ),
        201,
    )

@auth_bp.route("/login", methods=["POST"])
def login():
    d = LoginSchema().load(request.get_json() or {})
    u = User.query.filter_by(email=d["email"]).first()
    if not u:
        logger.warning("Login attempt with non-existent email: %s", d["email"])
        return jsonify({"error": "Invalid credentials."}), 401
    if not bcrypt.check_password_hash(u.password_hash, d["password"]):
        logger.warning("Invalid password for email: %s", d["email"])
        return jsonify({"error": "Invalid credentials."}), 401
    at, rtok = _create_tokens(u.id)
    primary_role = u.get_primary_role()
    logger.info("User %s logged in with role %s", d["email"], primary_role)
    return (
        jsonify(
            message=f"Welcome back, {u.name or u.email}.",
            access_token=at,
            refresh_token=rtok,
            role=primary_role,
            redirect_url=f"/{primary_role.lower()}dashboard"
        ),
        200,
    )

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    jti = get_jwt()["jti"]
    rt = RefreshToken.query.filter_by(token=jti).first()
    if not rt or rt.revoked:
        logger.warning("Invalid refresh token attempt: %s", jti)
        return jsonify({"error": "Invalid refresh token."}), 401
    uid = int(get_jwt_identity())
    at = create_access_token(
        identity=str(uid),
        expires_delta=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    )
    u = db.session.get(User, uid)
    primary_role = u.get_primary_role()
    logger.info("Token refreshed for user %s", uid)
    return jsonify(
        access_token=at,
        role=primary_role,
        redirect_url=f"/{primary_role.lower()}dashboard"
    ), 200

@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required(refresh=True)
def logout():
    jti = get_jwt()["jti"]
    rt = RefreshToken.query.filter_by(token=jti).first()
    if rt:
        rt.revoked = True
        db.session.commit()
        logger.info("User logged out, refresh token %s revoked", jti)
    return jsonify(message="Refresh token revoked."), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
@limiter.exempt  # Exempt /auth/me from rate limiting
def me():
    uid = int(get_jwt_identity())
    u = db.session.get(User, uid)
    if not u:
        logger.warning("User not found for ID: %s", uid)
        return jsonify({"error": "User not found."}), 404
    roles = [{"id": ur.role_id, "name": ur.role.name} for ur in u.user_roles]
    primary_role = u.get_primary_role()
    logger.info("Profile fetched for user %s", uid)
    return (
        jsonify(
            id=u.id,
            email=u.email,
            name=u.name,
            is_active=u.is_active,
            created_at=u.created_at.isoformat(),
            roles=roles,
            primary_role=primary_role,
            redirect_url=f"/{primary_role.lower()}dashboard"
        ),
        200,
    )

@auth_bp.route("/login/google")
def login_google():
    nonce = str(uuid.uuid4())
    session['nonce'] = nonce
    redirect_uri = url_for("auth.callback_google", _external=True)
    return oauth.google.authorize_redirect(
        redirect_uri,
        nonce=nonce
    )

@auth_bp.route("/callback/google")
def callback_google():
    stored_nonce = session.pop('nonce', None)
    if not stored_nonce:
        logger.error("No nonce found in session")
        return redirect("http://localhost:5173/auth/callback?error=Invalid OAuth state")
    try:
        tok = oauth.google.authorize_access_token()
        ui = oauth.google.parse_id_token(tok, nonce=stored_nonce)
    except OAuthError as e:
        logger.exception("Google OAuth failed: %s", str(e))
        return redirect("http://localhost:5173/auth/callback?error=Google login failed")
    em = ui.get("email")
    if not em:
        return redirect("http://localhost:5173/auth/callback?error=Google did not return an email")
    u = User.query.filter_by(email=em).first()
    pending_role = session.get('pending_role', 'User')
    if not u:
        rp = uuid.uuid4().hex
        ph = bcrypt.generate_password_hash(rp).decode()
        u = User(email=em, name=ui.get("name", ""), password_hash=ph)
        db.session.add(u)
        db.session.commit()
        role = Role.query.filter_by(name=pending_role).first()
        if not role:
            role = Role.query.filter_by(name="User").first()
        if role:
            db.session.add(UserRole(user_id=u.id, role_id=role.id))
            db.session.commit()
    at, rtok = _create_tokens(u.id)
    primary_role = u.get_primary_role()
    session.pop('pending_role', None)
    logger.info("Google OAuth login for %s with role %s", em, primary_role)
    return redirect(f"http://localhost:5173/auth/callback?access_token={at}&refresh_token={rtok}&role={primary_role}&redirect_url=/{primary_role.lower()}dashboard")

@auth_bp.route("/login/github")
def login_github():
    redirect_uri = url_for("auth.callback_github", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route("/callback/github")
def callback_github():
    try:
        tok = oauth.github.authorize_access_token()
        pr = oauth.github.get("user", token=tok).json()
        em = pr.get("email") or next(
            e["email"] for e in oauth.github.get("user/emails", token=tok).json() if e.get("primary")
        )
    except Exception as e:
        logger.exception("GitHub OAuth failed: %s", str(e))
        return redirect("http://localhost:5173/auth/callback?error=GitHub login failed")
    u = User.query.filter_by(email=em).first()
    pending_role = session.get('pending_role', 'User')
    if not u:
        rp = uuid.uuid4().hex
        ph = bcrypt.generate_password_hash(rp).decode()
        u = User(email=em, name=pr.get("name", ""), password_hash=ph)
        db.session.add(u)
        db.session.commit()
        role = Role.query.filter_by(name=pending_role).first()
        if not role:
            role = Role.query.filter_by(name="User").first()
        if role:
            db.session.add(UserRole(user_id=u.id, role_id=role.id))
            db.session.commit()
    at, rtok = _create_tokens(u.id)
    primary_role = u.get_primary_role()
    session.pop('pending_role', None)
    logger.info("GitHub OAuth login for %s with role %s", em, primary_role)
    return redirect(f"http://localhost:5173/auth/callback?access_token={at}&refresh_token={rtok}&role={primary_role}&redirect_url=/{primary_role.lower()}dashboard")

@auth_bp.route("/promote/<int:user_id>/<role_name>", methods=["POST"])
@jwt_required()
@requires_role("Admin")
def promote_user(user_id, role_name):
    u = db.session.get(User, user_id)
    if not u:
        logger.warning("User not found for promotion: %s", user_id)
        return jsonify({"error": "User not found."}), 404
    r = Role.query.filter_by(name=role_name).first()
    if not r:
        logger.warning("Role not found: %s", role_name)
        return jsonify({"error": "Role not found."}), 404
    if UserRole.query.filter_by(user_id=u.id, role_id=r.id).first():
        logger.info("User %s already has role %s", user_id, role_name)
        return jsonify({"error": "User already has that role."}), 409
    db.session.add(UserRole(user_id=u.id, role_id=r.id))
    db.session.commit()
    rs = [x.name for x in u.roles]
    logger.info("User %s promoted to %s", u.email, role_name)
    return (
        jsonify(
            message=f"{u.email} promoted to {role_name}",
            roles=rs,
        ),
        200,
    )