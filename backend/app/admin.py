import logging
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from . import bcrypt, db
from .models import(
    Category,
    Content,
    ContentStatusEnum,
    Role,
    User,
    UserRole,
)
from .utils import roles_required
logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
class CreateUserSchema(Schema):
    email = fields.Email(
        required=True,
        validate=validate.Length(max=128),
    )
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8),
            validate.Regexp(
                r".*\d.*",
                error="Password must contain at least one digit",
            ),
        ],
    )
    roles = fields.List(
        fields.Str(),
        required=True,
        validate=validate.Length(min=1),
    )
    name = fields.Str(
        load_default=None,
        validate=validate.Length(max=128),
    )
class CreateCategorySchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=64),
    )
    description = fields.Str(
        validate=validate.Length(max=256),
    )
class FlagContentSchema(Schema):
    reason = fields.Str(
        required=True,
        validate=validate.Length(max=256),
    )
@admin_bp.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError):
    return jsonify({"errors": err.messages}), 400
@admin_bp.route("/users", methods=["POST"])
@jwt_required()
@roles_required("Admin")
def create_user():
    data = CreateUserSchema().load(request.get_json() or {})
    chosen_name = data.get("name") or data["email"]
    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(
        email=data["email"],
        name=chosen_name,
        password_hash=password_hash,
    )
    db.session.add(user)
    try:
        db.session.flush()
        for role_name in data["roles"]:
            role = db.session.query(Role).filter_by(name=role_name).first()
            if not role:
                raise ValidationError({"roles": [f"Role '{role_name}' not found"]})
            db.session.add(UserRole(user_id=user.id, role_id=role.id))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists."}), 409
    except ValidationError as ve:
        db.session.rollback()
        return jsonify({"errors": ve.messages}), 400
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to create user")
        return jsonify({"error": "User creation failed."}), 500
    return jsonify({"message": "User created.", "id": user.id}), 201
@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@jwt_required()
@roles_required("Admin")
def deactivate_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    user.is_active = False
    db.session.commit()
    return jsonify({"message": f"User '{user.email}' deactivated."}), 200
@admin_bp.route("/users/<int:user_id>/promote/<role_name>", methods=["POST"])
@jwt_required()
@roles_required("Admin")
def promote_user(user_id: int, role_name: str):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    role = db.session.query(Role).filter_by(name=role_name).first()
    if not role:
        abort(404)
    existing = db.session.query(UserRole).filter_by(
        user_id=user.id, role_id=role.id
    ).first()
    if existing:
        return jsonify({"error": "User already has that role."}), 400
    db.session.add(UserRole(user_id=user.id, role_id=role.id))
    db.session.commit()
    return jsonify({"message": f"'{user.email}' promoted to '{role_name}'."}), 200
@admin_bp.route("/categories", methods=["POST"])
@jwt_required()
@roles_required("Admin", "TechWriter")
def create_category():
    data = CreateCategorySchema().load(request.get_json() or {})
    category = Category(
        name=data["name"],
        description=data.get("description"),
    )
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category already exists."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to create category")
        return jsonify({"error": "Category creation failed."}), 500
    return jsonify({"message": "Category created.", "id": category.id}), 201
@admin_bp.route("/contents/<int:content_id>/approve", methods=["POST"])
@jwt_required()
@roles_required("Admin")
def approve_content(content_id: int):
    content = db.session.get(Content, content_id)
    if not content:
        abort(404)
    content.status = ContentStatusEnum.Published
    db.session.commit()
    return jsonify({"message": f"Content {content.id} approved."}), 200
@admin_bp.route("/contents/<int:content_id>/flag", methods=["POST"])
@jwt_required()
@roles_required("Admin")
def flag_content(content_id: int):
    content = db.session.get(Content, content_id)
    if not content:
        abort(404)
    data = FlagContentSchema().load(request.get_json() or {})
    content.status = ContentStatusEnum.Flagged
    db.session.commit()
    return(
        jsonify({"message": f"Content {content.id} flagged.", "reason": data["reason"]}),
        200,
    )
@admin_bp.route("/contents/<int:content_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin")
def delete_content(content_id: int):
    content = db.session.get(Content, content_id)
    if not content:
        abort(404)
    db.session.delete(content)
    db.session.commit()
    return jsonify({"message": f"Content {content.id} deleted."}), 200