import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import Comment, Content
logger = logging.getLogger(__name__)
comments_bp = Blueprint("comments", __name__, url_prefix="/content/<int:content_id>/comments")
class CommentSchema(Schema):
    body = fields.Str(required=True, validate=validate.Length(min=1))
    parent_id = fields.Int(load_default=None)
@comments_bp.errorhandler(ValidationError)
def _handle_validation(err):
    return jsonify({"errors": err.messages}), 400
@comments_bp.route("", methods=["POST"])
@jwt_required()
def create_comment(content_id):
    user_id = int(get_jwt_identity())
    Content.query.get_or_404(content_id)
    data = CommentSchema().load(request.get_json() or {})
    parent_id = data.get("parent_id")
    if parent_id:
        if not Comment.query.filter_by(id=parent_id, content_id=content_id).first():
            return jsonify({"error": "Invalid parent comment"}), 400
    c = Comment(content_id=content_id, user_id=user_id, body=data["body"], parent_id=parent_id)
    db.session.add(c)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to save comment content=%s user=%s", content_id, user_id)
        return jsonify({"error": "Could not create comment"}), 500
    return jsonify({"id": c.id}), 201
@comments_bp.route("", methods=["GET"])
def list_comments(content_id):
    Content.query.get_or_404(content_id)
    all_comments = Comment.query.filter_by(content_id=content_id).order_by(Comment.created_at).all()
    m = {c.id: {"id": c.id, "user_id": c.user_id, "body": c.body,
                "parent_id": c.parent_id, "created_at": c.created_at.isoformat(),
                "replies": []} for c in all_comments}
    roots = []
    for c in all_comments:
        node = m[c.id]
        if c.parent_id:
            m[c.parent_id]["replies"].append(node)
        else:
            roots.append(node)
    return jsonify(roots), 200