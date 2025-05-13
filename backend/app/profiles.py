import logging
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from . import db
from .models import UserProfile
from .utils import roles_required

logger = logging.getLogger(__name__)
profile_bp = Blueprint("profile", __name__, url_prefix="/profiles")
CORS(profile_bp, origins=["http://localhost:5173"], supports_credentials=True)

class ProfileSchema(Schema):
    name = fields.Str(validate=validate.Length(max=128))
    bio = fields.Str(validate=validate.Length(max=1024))
    social_links = fields.Str(validate=validate.Length(max=512), allow_none=True)

@profile_bp.errorhandler(ValidationError)
def on_validation_error(err):
    return jsonify({"errors": err.messages}), 422

@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({}), 200
    
    avatar_url = None
    if profile.avatar_url:
        if profile.avatar_url.startswith('/'):
            avatar_url = f"{request.scheme}://{request.host}{profile.avatar_url}"
            logger.info("Avatar URL for user_id=%s: %s", user_id, avatar_url)
        else:
            avatar_url = profile.avatar_url

    return jsonify({
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name or "",
        "bio": profile.bio or "",
        "avatar_url": avatar_url,
        "social_links": profile.social_links or "",
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }), 200

@profile_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_my_profile():
    user_id = int(get_jwt_identity())
    
    data = request.form.to_dict()
    file = request.files.get('avatar')
    
    validated_data = ProfileSchema().load(data)
    
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
        
        for key, value in validated_data.items():
            setattr(profile, key, value)
        
        if file:
            upload_dir = current_app.config['UPLOAD_FOLDER']  # Use config-defined folder
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"avatar_{user_id}_{timestamp}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            
            file.save(file_path)
            logger.info("File saved at: %s", file_path)
            
            # Store relative path starting with '/uploads/'
            profile.avatar_url = f"/uploads/{filename}"
        
        db.session.commit()
        logger.info("Profile updated successfully for user_id=%s", user_id)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception("Failed to update profile for user_id=%s: %s", user_id, str(e))
        return jsonify({"error": "Could not update profile"}), 500
    except Exception as e:
        logger.exception("Error during file upload for user_id=%s: %s", user_id, str(e))
        return jsonify({"error": "Error uploading file"}), 500
    
    avatar_url = None
    if profile.avatar_url:
        if profile.avatar_url.startswith('/'):
            avatar_url = f"{request.scheme}://{request.host}{profile.avatar_url}"
            logger.info("Avatar URL for user_id=%s: %s", user_id, avatar_url)
        else:
            avatar_url = profile.avatar_url

    return jsonify({
        "message": "Profile updated",
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name or "",
        "bio": profile.bio or "",
        "avatar_url": avatar_url,
        "social_links": profile.social_links or "",
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }), 200

@profile_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@roles_required("Admin")
def get_user_profile(user_id):
    profile = UserProfile.query.filter_by(user_id=user_id).first_or_404()
    
    avatar_url = None
    if profile.avatar_url:
        if profile.avatar_url.startswith('/'):
            avatar_url = f"{request.scheme}://{request.host}{profile.avatar_url}"
            logger.info("Avatar URL for user_id=%s: %s", user_id, avatar_url)
        else:
            avatar_url = profile.avatar_url

    return jsonify({
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name or "",
        "bio": profile.bio or "",
        "avatar_url": avatar_url,
        "social_links": profile.social_links or "",
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }), 200