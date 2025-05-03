import logging
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)
categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

class CategorySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    description = fields.Str(allow_none=True)

@categories_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify({"errors": err.messages}), 400

@categories_bp.route("", methods=["GET"])
def list_categories():
    from . import db
    from .models import Category
    cats = Category.query.order_by(Category.name).all()
    return jsonify([
        {"id": c.id, "name": c.name, "description": c.description}
        for c in cats
    ]), 200

@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    from . import db
    from .models import Category
    c = Category.query.get_or_404(category_id)
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description
    }), 200

@categories_bp.route("", methods=["POST"])
@jwt_required()
def create_category():
    from . import db
    from .models import Category
    from .utils import roles_required
    from .audit import audit
    @roles_required("Admin", "TechWriter")
    @audit("create_category", target_type="Category", target_id_arg="id")
    def inner():
        data = CategorySchema().load(request.get_json() or {})
        user_id = int(get_jwt_identity())
        c = Category(
            name=data["name"],
            description=data.get("description"),
            created_by=user_id
        )
        db.session.add(c)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Category name already exists."}), 409
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("create_category failed by user %s", user_id)
            return jsonify({"error": "Category creation failed."}), 500
        return jsonify({"id": c.id, "message": "Category created."}), 201
    return inner()

@categories_bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
def update_category(category_id):
    from . import db
    from .models import Category
    from .utils import roles_required
    from .audit import audit
    @roles_required("Admin", "TechWriter")
    @audit("update_category", target_type="Category", target_id_arg="category_id")
    def inner():
        c = Category.query.get_or_404(category_id)
        data = CategorySchema().load(request.get_json() or {}, partial=True)
        if "name" in data:
            c.name = data["name"]
        if "description" in data:
            c.description = data["description"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Category name already exists."}), 409
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("update_category failed for %s", category_id)
            return jsonify({"error": "Category update failed."}), 500
        return jsonify({"id": c.id, "message": "Category updated."}), 200
    return inner()

@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    from . import db
    from .models import Category
    from .utils import roles_required
    from .audit import audit
    @roles_required("Admin", "TechWriter")
    @audit("delete_category", target_type="Category", target_id_arg="category_id")
    def inner():
        c = Category.query.get_or_404(category_id)
        db.session.delete(c)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("delete_category failed for %s", category_id)
            return jsonify({"error": "Category deletion failed."}), 500
        return jsonify({"message": "Category deleted."}), 200
    return inner()