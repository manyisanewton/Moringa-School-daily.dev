import logging
from typing import Dict, Any, List
from flask import Blueprint, request, jsonify, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os
from . import db, socketio
from .audit import audit
from .models import (
    Category,
    Comment,
    Content,
    ContentStatusEnum,
    ContentTypeEnum,
    Notification,
    Subscription,
    User,
    Role,
    Reaction,
)
from .utils import allowed_file
from flask_socketio import emit

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
        load_default=ContentStatusEnum.Pending.value,
        validate=validate.OneOf([cs.value for cs in ContentStatusEnum]),
    )
    category_id = fields.Int(load_default=None)
    category = fields.Str(load_default=None)  # Add category name field

class CommentSchema(Schema):
    body = fields.Str(required=True)
    parent_id = fields.Int(load_default=None)

def _require_writer_or_admin(user: User) -> None:
    roles = {r.name for r in user.roles}
    logger.info(f"User roles: {roles}")  # Log roles for debugging
    if "TechWriter" not in roles and "Admin" not in roles:
        abort(403, description="Insufficient permissions")

def _send_notifications(content: Content, message: str = None) -> None:
    # Notify subscribers
    subs = Subscription.query.filter_by(category_id=content.category_id).all()
    for sub in subs:
        type_label = content.content_type.value
        msg = message or f"New {type_label} in {content.category.name}: {content.title}"
        notification = Notification(user_id=sub.user_id, content_id=content.id, message=msg)
        db.session.add(notification)
        socketio.emit('new_notification', {
            'id': notification.id,
            'type': type_label,
            'message': msg,
            'subMessage': f'[{type_label} Link]',
            'time': notification.created_at.isoformat(),
            'read': False
        }, room=str(sub.user_id))
    
    # Notify admins about pending content
    admin_role = Role.query.filter_by(name="Admin").first()
    if admin_role:
        admins = User.query.filter(User.roles.any(id=admin_role.id)).all()
        for admin in admins:
            msg = f"New content pending approval: {content.title}"
            notification = Notification(user_id=admin.id, content_id=content.id, message=msg)
            db.session.add(notification)
            socketio.emit('new_notification', {
                'id': notification.id,
                'type': 'System',
                'message': msg,
                'subMessage': '[Review Content]',
                'time': notification.created_at.isoformat(),
                'read': False
            }, room=str(admin.id))
    
    # Notify the author when content is submitted
    user = db.session.get(User, content.author_id)
    if user:
        msg = f"Your content '{content.title}' has been submitted for approval."
        notification = Notification(user_id=user.id, content_id=content.id, message=msg)
        db.session.add(notification)
        socketio.emit('new_notification', {
            'id': notification.id,
            'type': 'System',
            'message': msg,
            'subMessage': '[View Content]',
            'time': notification.created_at.isoformat(),
            'read': False
        }, room=str(user.id))
    
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
    # Temporarily bypass role check for debugging
    # _require_writer_or_admin(user)

    # Handle form data and file upload
    data = request.form.to_dict()
    file = request.files.get('file')

    # Validate form data
    validated_data = ContentSchema().load(data)

    # Handle category: Use category name if provided, otherwise fall back to category_id
    category_id = validated_data.get("category_id")
    category_name = data.get("category")  # Get category name from form data

    if category_name:
        # Look up or create the category based on the name
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(
                name=category_name,
                description=f"Content related to {category_name.lower()}.",
                created_by=user_id
            )
            db.session.add(category)
            db.session.commit()
        category_id = category.id
    elif category_id is not None and not db.session.get(Category, category_id):
        abort(404, description="Category not found")

    # Handle file upload
    media_url = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        media_url = f"http://localhost:5000/uploads/{filename}"

    # Map content type based on file type
    content_type = validated_data["content_type"]
    if file:
        if file.mimetype.startswith('image'):
            content_type = ContentTypeEnum.article
        elif file.mimetype == 'application/pdf':
            content_type = ContentTypeEnum.article
        elif file.mimetype == 'video/mp4':
            content_type = ContentTypeEnum.video

    content = Content(
        title=validated_data["title"],
        body=validated_data["body"],
        media_url=media_url,
        content_type=content_type,
        status=ContentStatusEnum.Pending,
        author_id=user_id,
        category_id=category_id
    )
    db.session.add(content)
    try:
        db.session.commit()
        _send_notifications(content, f"New {content.content_type.value} submitted for approval in {content.category.name}: {content.title}")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception("Content creation failed: %s", str(e))
        return jsonify(error="Content creation failed."), 500
    return jsonify(id=content.id, status=content.status.value), 201

@content_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    if "file" not in request.files:
        return jsonify(error="No file part"), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(error="No selected file"), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        media_url = f"http://localhost:5000/uploads/{filename}"
        return jsonify(media_url=media_url), 200
    return jsonify(error="File type not allowed"), 400

@content_bp.route("", methods=["GET"])
def list_content():
    user_id = request.args.get("user_id", type=int)
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get(
        "per_page", type=int, default=current_app.config.get("CONTENT_PER_PAGE", 10)
    )
    per_page = min(per_page, current_app.config.get("MAX_CONTENT_PER_PAGE", 50))
    
    query = Content.query
    if user_id:
        query = query.filter_by(author_id=user_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [
        {
            "id": c.id,
            "title": c.title,
            "body": c.body,
            "media_url": c.media_url,
            "content_type": c.content_type.value,
            "status": c.status.value,
            "category_id": c.category_id,
            "category_name": c.category.name if c.category else None,
            "author_id": c.author_id,
            "created_at": c.created_at.isoformat(),
        }
        for c in pagination.items
    ]
    return jsonify({
        "items": items,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }), 200

@content_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_techwriter_stats():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id) or abort(404, description="User not found")
    _require_writer_or_admin(user)

    # Calculate stats
    total_posts = Content.query.filter_by(author_id=user_id).count()
    posts_pending = Content.query.filter_by(author_id=user_id, status=ContentStatusEnum.Pending).count()
    likes = db.session.query(func.count(Reaction.id)).filter(
        Reaction.content_id.in_(
            db.session.query(Content.id).filter_by(author_id=user_id)
        ),
        Reaction.type == ReactionTypeEnum.like
    ).scalar() or 0
    comments = Comment.query.join(Content).filter(Content.author_id == user_id).count()

    return jsonify({
        "totalPosts": total_posts,
        "postsPending": posts_pending,
        "likes": likes,
        "comments": comments
    }), 200

@content_bp.route("/flagged", methods=["GET"])
@jwt_required()
def get_flagged_content():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id) or abort(404, description="User not found")
    _require_writer_or_admin(user)

    flagged_content = Content.query.filter(
        Content.author_id == user_id,
        Content.status == ContentStatusEnum.Flagged
    ).all()

    items = [
        {
            "id": c.id,
            "type": c.content_type.value,
            "title": c.title,
            "reason": c.flags[0].reason if c.flags else "No reason provided",
        }
        for c in flagged_content
    ]
    return jsonify({"items": items}), 200

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
            "status": c.status.value,
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
    is_writer = any(r.name == "TechWriter" for r in user.roles)
    if not (is_author or is_admin or is_writer):
        abort(403, description="Insufficient permissions")
    data = ContentSchema().load(request.get_json() or {}, partial=True)
    if "category_id" in data and data["category_id"] is not None:
        if not db.session.get(Category, data["category_id"]):
            abort(404, description="Category not found")
    if "content_type" in data:
        data["content_type"] = ContentTypeEnum(data["content_type"])
    if "status" in data:
        data["status"] = ContentStatusEnum(data["status"])
        if data["status"] == ContentStatusEnum.Published.value:
            if not (is_writer or is_admin):
                abort(403, description="Only TechWriter or Admin can approve content")
            _send_notifications(content, "Content has been approved")
    for field, value in data.items():
        setattr(content, field, value)
    try:
        db.session.commit()
        socketio.emit('content_status_update', {'content_id': content.id, 'status': content.status.value}, broadcast=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception("Content update failed: %s", str(e))
        return jsonify(error="Could not update content."), 500
    return jsonify(id=content.id, status=content.status), 200

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
    
    # Notify before deleting
    notification_message = f"Content '{content.title}' has been deleted by {user.name}"
    _send_notifications(content, notification_message)

    db.session.delete(content)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception("Content deletion failed: %s", str(e))
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
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception("Failed to add comment %s by %s: %s", content_id, uid, str(e))
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