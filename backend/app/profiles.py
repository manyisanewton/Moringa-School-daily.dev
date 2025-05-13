import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import UserProfile
from .utils import roles_required
logger = logging.getLogger(__name__)
profile_bp = Blueprint("profile", __name__, url_prefix="/profiles")
class ProfileSchema(Schema):
    name = fields.Str(validate=validate.Length(max=128))
    bio = fields.Str(validate=validate.Length(max=1024))
    avatar_url = fields.Url(allow_none=True)
    social_links = fields.Str(validate=validate.Length(max=512), allow_none=True)
@profile_bp.errorhandler(ValidationError)
def on_validation_error(err):
    return jsonify({"errors": err.messages}), 400
@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({}), 200
    return jsonify({
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "social_links": profile.social_links,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }), 200
@profile_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_my_profile():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    data = ProfileSchema().load(payload)
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id, **data)
            db.session.add(profile)
        else:
            for key, value in data.items():
                setattr(profile, key, value)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to update profile for user_id=%s", user_id)
        return jsonify({"error": "Could not update profile"}), 500
    return jsonify({
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "social_links": profile.social_links,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }), 200
@profile_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@roles_required("Admin")
def get_user_profile(user_id):
    profile = UserProfile.query.filter_by(user_id=user_id).first_or_404()
    return jsonify({
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "social_links": profile.social_links,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }), 200