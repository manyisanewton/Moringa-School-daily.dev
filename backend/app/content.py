import logging
from typing import Dict, Any, List
from flask import Blueprint, request, jsonify, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .audit import audit
from .models import(
    Category,
    Comment,
    Content,
    ContentStatusEnum,
    ContentTypeEnum,
    Notification,
    Subscription,
    User,
)
logger = logging.getLogger(__name__)
content_bp = Blueprint("content", __name__, url_prefix="/content")
class ContentSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(max=256))
    body = fields.Str(load_default="")
    media_url = fields.Url(allow_none=True, load_default=None)
    content_type = fields.Str(
        required=True,
        validate=validate.OneOf([ct.value for ct in ContentTypeEnum]),
    )
    status = fields.Str(
        load_default=ContentStatusEnum.Draft.value,
        validate=validate.OneOf([cs.value for cs in ContentStatusEnum]),
    )
    category_id = fields.Int(load_default=None)
class CommentSchema(Schema):
    body = fields.Str(required=True)
    parent_id = fields.Int(load_default=None)
def _require_writer_or_admin(user: User) -> None:
    roles = {r.name for r in user.roles}
    if "TechWriter" not in roles and "Admin" not in roles:
        abort(403, description="Insufficient permissions")
def _send_notifications(content: Content) -> None:
    subs = Subscription.query.filter_by(category_id=content.category_id).all()
    for sub in subs:
        type_label = content.content_type.value
        message = f"New {type_label} in {content.category.name}: {content.title}"
        db.session.add(
            Notification(user_id=sub.user_id, content_id=content.id, message=message)
        )
    db.session.commit()
@content_bp.errorhandler(ValidationError)
def handle_validation(err: ValidationError):
    return jsonify(errors=err.messages), 400
@content_bp.route("", methods=["POST"])
@jwt_required()
@audit("create_content", target_type="Content", target_id_arg="id")
def create_content():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id) or abort(404, description="User not found")
    _require_writer_or_admin(user)
    data = ContentSchema().load(request.get_json() or {})
    cat_id = data.get("category_id")
    if cat_id is not None and not db.session.get(Category, cat_id):
        abort(404, description="Category not found")
    data["content_type"] = ContentTypeEnum(data["content_type"])
    data["status"] = ContentStatusEnum(data["status"])
    content = Content(author_id=user_id, **data)
    db.session.add(content)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(error="Content creation failed."), 500
    if content.status == ContentStatusEnum.Published:
        _send_notifications(content)
    return jsonify(id=content.id), 201
@content_bp.route("", methods=["GET"])
def list_content():
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get(
        "per_page", type=int, default=current_app.config.get("CONTENT_PER_PAGE", 10)
    )
    per_page = min(per_page, current_app.config.get("MAX_CONTENT_PER_PAGE", 50))
    pagination = Content.query.paginate(page=page, per_page=per_page, error_out=False)
    items = [
        {
            "id": c.id,
            "title": c.title,
            "body": c.body,
            "media_url": c.media_url,
            "content_type": c.content_type.value,
            "status": c.status.value,
            "category_id": c.category_id,
            "author_id": c.author_id,
            "created_at": c.created_at.isoformat(),
        }
        for c in pagination.items
    ]
    return jsonify(items), 200
@content_bp.route("/<int:content_id>", methods=["GET"])
def get_content(content_id: int):
    content = db.session.get(Content, content_id) or abort(404, description="Content not found")
    return jsonify(
        {
            "id": content.id,
            "title": content.title,
            "body": content.body,
            "media_url": content.media_url,
            "content_type": content.content_type.value,
            "status": content.status.value,
            "category_id": content.category_id,
            "author_id": content.author_id,
            "created_at": content.created_at.isoformat(),
        }
    ), 200
@content_bp.route("/<int:content_id>", methods=["PUT"])
@jwt_required()
@audit("update_content", target_type="Content", target_id_arg="content_id")
def update_content(content_id: int):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id) or abort(404, description="User not found")
    content = db.session.get(Content, content_id) or abort(404, description="Content not found")
    is_author = content.author_id == user_id
    is_admin = any(r.name == "Admin" for r in user.roles)
    if not (is_author or is_admin):
        abort(403, description="Insufficient permissions")
    data = ContentSchema().load(request.get_json() or {}, partial=True)
    if "category_id" in data and data["category_id"] is not None:
        if not db.session.get(Category, data["category_id"]):
            abort(404, description="Category not found")
    if "content_type" in data:
        data["content_type"] = ContentTypeEnum(data["content_type"])
    if "status" in data:
        data["status"] = ContentStatusEnum(data["status"])
    for field, value in data.items():
        setattr(content, field, value)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(error="Could not update content."), 500
    if content.status == ContentStatusEnum.Published:
        _send_notifications(content)
    return jsonify(id=content.id), 200
@content_bp.route("/<int:content_id>", methods=["DELETE"])
@jwt_required()
@audit("delete_content", target_type="Content", target_id_arg="content_id")
def delete_content(content_id: int):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id) or abort(404, description="User not found")
    content = db.session.get(Content, content_id) or abort(404, description="Content not found")
    is_author = content.author_id == user_id
    is_admin = any(r.name == "Admin" for r in user.roles)
    if not (is_author or is_admin):
        abort(403, description="Insufficient permissions")
    db.session.delete(content)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(error="Could not delete content."), 500
    return jsonify(message="Content deleted"), 200
@content_bp.route("/<int:content_id>/comments", methods=["POST"])
@jwt_required()
@audit("add_comment", target_type="Comment", target_id_arg="id")
def add_comment(content_id: int):
    uid = int(get_jwt_identity())
    if not db.session.get(Content, content_id):
        abort(404, description="Content not found")
    data = CommentSchema().load(request.get_json() or {})
    if data.get("parent_id"):
        parent = Comment.query.filter_by(id=data["parent_id"], content_id=content_id).first()
        if not parent:
            abort(400, description="Invalid parent comment")
    comment = Comment(
        content_id=content_id, user_id=uid, body=data["body"], parent_id=data.get("parent_id")
    )
    db.session.add(comment)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to add comment %s by %s", content_id, uid)
        return jsonify(error="Could not add comment."), 500
    return jsonify(id=comment.id), 201
@content_bp.route("/<int:content_id>/comments", methods=["GET"])
def list_comments(content_id: int):
    if not db.session.get(Content, content_id):
        abort(404, description="Content not found")
    comments = Comment.query.filter_by(content_id=content_id).order_by(Comment.created_at).all()
    nodes: Dict[int, Dict[str, Any]] = {}
    for c in comments:
        nodes[c.id] = {
            "id": c.id,
            "body": c.body,
            "user_id": c.user_id,
            "parent_id": c.parent_id,
            "created_at": c.created_at.isoformat(),
            "replies": [],
        }
    tree: List[Dict[str, Any]] = []
    for c in comments:
        node = nodes[c.id]
        if c.parent_id:
            parent_node = nodes.get(c.parent_id)
            if parent_node:
                parent_node["replies"].append(node)
        else:
            tree.append(node)
    return jsonify(tree), 200