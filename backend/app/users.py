import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import User, UserProfile, UserRole, Role
from .utils import roles_required
from .audit import audit
logger = logging.getLogger(__name__)
user_bp = Blueprint("users", __name__, url_prefix="/users")
class ProfileSchema(Schema):
    name = fields.Str(validate=validate.Length(max=128))
    bio = fields.Str()
    avatar_url = fields.Url()
    social_links = fields.Str(validate=validate.Length(max=512))
@user_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(errors=err.messages), 400
def _profile_to_dict(u: User):
    profile = u.profile or {}
    roles = [role.name for role in u.roles]
    return {
        "user_id": u.id,
        "id": u.id,
        "email": u.email,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat(),
        "name": getattr(profile, "name", None),
        "bio": getattr(profile, "bio", None),
        "avatar_url": getattr(profile, "avatar_url", None),
        "social_links": getattr(profile, "social_links", None),
        "roles": roles,
        "primary_role": u.get_primary_role()  # Include primary role
    }
@user_bp.route("/me/profile", methods=["GET"])
@jwt_required()
@audit("get_profile", target_type="UserProfile", target_id_arg="id")
def get_my_profile():
    uid = int(get_jwt_identity())
    u = User.query.get_or_404(uid)
    if not u.profile:
        u.profile = UserProfile(user_id=uid)
        db.session.add(u.profile)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
    return jsonify(_profile_to_dict(u)), 200
@user_bp.route("/me/profile", methods=["PATCH", "PUT"])
@jwt_required()
@audit("update_profile", target_type="UserProfile", target_id_arg="id")
def update_my_profile():
    uid = int(get_jwt_identity())
    data = ProfileSchema().load(request.get_json() or {}, partial=True)
    u = User.query.get_or_404(uid)
    if not u.profile:
        u.profile = UserProfile(user_id=uid)
        db.session.add(u.profile)
    for field in ("name", "bio", "avatar_url", "social_links"):
        if field in data:
            setattr(u.profile, field, data[field])
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed updating profile for user_id=%s", uid)
        return jsonify(error="Could not update profile."), 500
    return jsonify(_profile_to_dict(u)), 200
@user_bp.route("/<int:user_id>/promote/<role_name>", methods=["POST"])
@jwt_required()
@roles_required("Admin")
@audit("promote_user", target_type="User", target_id_arg="user_id")
def promote_user(user_id, role_name):
    u = User.query.get_or_404(user_id)
    r = Role.query.filter_by(name=role_name).first_or_404()
    if UserRole.query.filter_by(user_id=u.id, role_id=r.id).first():
        return jsonify(error="User already has that role."), 409
    db.session.add(UserRole(user_id=u.id, role_id=r.id))
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed promoting user_id=%s to %s", user_id, role_name)
        return jsonify(error="Promotion failed."), 500
    roles = [role.name for role in u.roles]
    return jsonify(
        message=f"{u.email} promoted to {role_name}",
        roles=roles,
        primary_role=u.get_primary_role()  # Include primary role
    ), 200