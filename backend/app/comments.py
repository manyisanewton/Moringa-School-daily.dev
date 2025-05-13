import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from . import db
from .models import Comment, Post, User
from .notifications import notify_new_comment  # Import notification helper

logger = logging.getLogger(__name__)
comments_bp = Blueprint(
    "comments",
    __name__,
    url_prefix="/categories/<int:post_id>/comments"
)
EDIT_WINDOW = timedelta(minutes=30)

class CommentSchema(Schema):
    body = fields.Str(required=True, validate=validate.Length(min=1))
    parent_id = fields.Int(load_default=None)

class CommentService:
    @staticmethod
    def get_post_or_404(post_id: int) -> Post:
        post = db.session.get(Post, post_id)
        if not post:
            abort(404, description="Post not found")
        return post

    @staticmethod
    def get_comment_or_404(post_id: int, comment_id: int) -> Comment:
        comment = Comment.query.filter_by(
            id=comment_id, post_id=post_id
        ).first()
        if not comment:
            abort(404, description="Comment not found")
        return comment

    @staticmethod
    def is_admin(user: User) -> bool:
        return any(r.name == "Admin" for r in user.roles)

    @staticmethod
    def can_edit(comment: Comment, user_id: int) -> bool:
        if comment.user_id != user_id:
            return False
        return datetime.utcnow() <= comment.created_at + EDIT_WINDOW

    @staticmethod
    def can_delete(comment: Comment, user: User) -> bool:
        return comment.user_id == user.id or CommentService.is_admin(user)

@comments_bp.errorhandler(ValidationError)
def handle_bad_payload(err: ValidationError):
    return jsonify({"errors": err.messages}), 400

@comments_bp.errorhandler(403)
def handle_forbidden(err: HTTPException):
    return jsonify({"error": err.description}), 403

@comments_bp.errorhandler(404)
def handle_not_found(err: HTTPException):
    return jsonify({"error": err.description}), 404

@comments_bp.route("", methods=["POST"])
@jwt_required()
def create_comment(post_id: int):
    user_id = int(get_jwt_identity())
    post = CommentService.get_post_or_404(post_id)
    data = CommentSchema().load(request.get_json() or {})
    parent_id = data.get("parent_id")
    if parent_id:
        exists = Comment.query.filter_by(
            id=parent_id, post_id=post_id
        ).first()
        if not exists:
            abort(400, description="Invalid parent comment")
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        body=data["body"],
        parent_id=parent_id,
    )
    db.session.add(comment)
    try:
        db.session.commit()
        post.comments = Comment.query.filter_by(post_id=post_id).count()
        db.session.commit()
        notify_new_comment(comment)  # Trigger notification for new comment
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to create comment %s by %s", post_id, user_id)
        abort(500, description="Could not create comment")
    return jsonify({"id": comment.id}), 201

@comments_bp.route("", methods=["GET"])
def list_comments(post_id: int):
    CommentService.get_post_or_404(post_id)
    all_comments = Comment.query.filter_by(
        post_id=post_id
    ).order_by(Comment.created_at).all()
    nodes: Dict[int, Dict[str, Any]] = {
        c.id: {
            "id": c.id,
            "user_id": c.user_id,
            "body": c.body,
            "parent_id": c.parent_id,
            "created_at": c.created_at.isoformat(),
            "replies": [],
        }
        for c in all_comments
    }
    threads: List[Dict[str, Any]] = []
    for c in all_comments:
        node = nodes[c.id]
        if c.parent_id:
            nodes[c.parent_id]["replies"].append(node)
        else:
            threads.append(node)

    return jsonify(threads), 200

@comments_bp.route("/<int:comment_id>", methods=["PUT"])
@jwt_required()
def edit_comment(post_id: int, comment_id: int):
    user_id = int(get_jwt_identity())
    comment = CommentService.get_comment_or_404(post_id, comment_id)
    if not CommentService.can_edit(comment, user_id):
        abort(403, description="You may not edit this comment")
    data = CommentSchema().load(request.get_json() or {})
    comment.body = data["body"]
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to edit comment %s by %s", comment_id, user_id)
        abort(500, description="Could not edit comment")
    return jsonify({"id": comment.id, "body": comment.body}), 200

@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(post_id: int, comment_id: int):
    user_id = int(get_jwt_identity())
    comment = CommentService.get_comment_or_404(post_id, comment_id)
    user = db.session.get(User, user_id)
    if not user:
        abort(404, description="User not found")
    if not CommentService.can_delete(comment, user):
        abort(403, description="You may not delete this comment")
    try:
        db.session.delete(comment)
        db.session.commit()
        post = db.session.get(Post, post_id)
        post.comments = Comment.query.filter_by(post_id=post_id).count()
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to delete comment %s by %s", comment_id, user_id)
        abort(500, description="Could not delete comment")
    return jsonify({"message": "Comment deleted"}), 200