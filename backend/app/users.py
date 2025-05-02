import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import User, UserProfile, UserRole, Role
from .utils import roles_required
from .audit import audit
logger=logging.getLogger(__name__)
user_bp=Blueprint('users',__name__,url_prefix='/users')
class ProfileSchema(Schema):
    name=fields.Str(validate=validate.Length(max=128))
    bio=fields.Str()
    avatar_url=fields.Url()
    social_links=fields.Str(validate=validate.Length(max=512))
@user_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(errors=err.messages),400
def _profile_to_dict(user:User):
    prof=user.profile or UserProfile(user_id=user.id)
    return{
        'id':user.id,
        'email':user.email,
        'is_active':user.is_active,
        'created_at':user.created_at.isoformat(),
        'name':prof.name,
        'bio':prof.bio,
        'avatar_url':prof.avatar_url,
        'social_links':prof.social_links
    }
@user_bp.route('/me/profile',methods=['GET'])
@jwt_required()
@audit("get_profile",target_type="UserProfile",target_id_arg="user_id")
def get_my_profile():
    uid=int(get_jwt_identity())
    user=User.query.get_or_404(uid)
    if not user.profile:
        user.profile=UserProfile(user_id=uid)
        db.session.add(user.profile)
        db.session.commit()
    return jsonify(_profile_to_dict(user)),200
@user_bp.route('/me/profile',methods=['PUT'])
@jwt_required()
@audit("update_profile",target_type="UserProfile",target_id_arg="user_id")
def update_my_profile():
    uid=int(get_jwt_identity())
    data=ProfileSchema().load(request.get_json() or {},partial=True)
    user=User.query.get_or_404(uid)
    if not user.profile:
        user.profile=UserProfile(user_id=uid)
        db.session.add(user.profile)
    for field in('name','bio','avatar_url','social_links'):
        if field in data:
            setattr(user.profile,field,data[field])
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed updating profile for user_id=%s",uid)
        return jsonify(error='Could not update profile.'),500
    return jsonify(_profile_to_dict(user)),200
@user_bp.route('/<int:user_id>/promote/<role_name>',methods=['POST'])
@jwt_required()
@roles_required('Admin')
@audit("promote_user",target_type="User",target_id_arg="user_id")
def promote_user(user_id,role_name):
    user=User.query.get_or_404(user_id)
    role=Role.query.filter_by(name=role_name).first_or_404()
    if UserRole.query.filter_by(user_id=user.id,role_id=role.id).first():
        return jsonify(error='User already has that role.'),409
    db.session.add(UserRole(user_id=user.id,role_id=role.id))
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed promoting user_id=%s to %s",user_id,role_name)
        return jsonify(error='Promotion failed.'),500
    roles_list=[r.name for r in user.roles]
    return jsonify(message=f'{user.email} promoted to {role_name}',roles=roles_list),200