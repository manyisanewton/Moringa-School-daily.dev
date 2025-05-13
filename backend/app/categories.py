import logging
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import Schema, ValidationError, fields, validate, EXCLUDE
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from . import db
from .audit import audit
from .models import Category
from .utils import roles_required
logger = logging.getLogger(__name__)
categories_bp = Blueprint("categories", __name__, url_prefix="/categories")
class CategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE
    name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    description = fields.Str(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=256),
    )
@categories_bp.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError):
    return jsonify({"errors": err.messages}), 400
@categories_bp.route("", methods=["GET"])
def list_categories():
    cats = Category.query.order_by(Category.name).all()
    return jsonify([
        {"id": c.id, "name": c.name, "description": c.description}
        for c in cats
    ]), 200
@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    c = Category.query.get_or_404(category_id)
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
    }), 200
@categories_bp.route("", methods=["POST"])
@jwt_required()
@roles_required("Admin", "TechWriter")
@audit("create_category", target_type="Category", target_id_arg="id")
def create_category():
    data = CategorySchema().load(request.get_json() or {})
    if Category.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Category name already exists."}), 409
    c = Category(
        name=data["name"],
        description=data["description"],
        created_by=int(get_jwt_identity()),
    )
    db.session.add(c)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("create_category failed")
        return jsonify({"error": "Category creation failed."}), 500
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
    }), 201
@categories_bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
@roles_required("Admin", "TechWriter")
@audit("update_category", target_type="Category", target_id_arg="category_id")
def update_category(category_id):
    c = Category.query.get_or_404(category_id)
    data = CategorySchema(partial=True).load(request.get_json() or {})
    if "name" not in data:
        return jsonify({"errors": {"name": ["Missing data for required field."]}}), 400
    if (
        data["name"] != c.name
        and Category.query.filter(Category.name == data["name"],
                                  Category.id != category_id).first()
    ):
        return jsonify({"error": "Category name already exists."}), 409
    c.name = data["name"]
    if "description" in data:
        c.description = data["description"]
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("update_category failed")
        return jsonify({"error": "Category update failed."}), 500
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
    }), 200
@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin", "TechWriter")
@audit("delete_category", target_type="Category", target_id_arg="category_id")
def delete_category(category_id):
    c = Category.query.get_or_404(category_id)
    db.session.delete(c)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("delete_category failed")
        return jsonify({"error": "Category deletion failed."}), 500
    return jsonify({"message": "Category deleted."}), 200