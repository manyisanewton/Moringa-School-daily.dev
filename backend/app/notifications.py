import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, decode_token
from sqlalchemy.exc import SQLAlchemyError
from flask_socketio import emit, disconnect
from . import db, socketio
from .models import Notification, Post, Comment, Like

logger = logging.getLogger(__name__)
notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

# Helper function to create and emit a notification
def create_and_emit_notification(user_id, message, content_id=None):
    notification = Notification(
        user_id=user_id,
        content_id=content_id,
        message=message,
        is_read=False
    )
    db.session.add(notification)
    try:
        db.session.commit()
        # Emit the notification to the user via SocketIO
        socketio.emit('new_notification', {
            'id': notification.id,
            'type': 'System',
            'message': message,
            'subMessage': message,
            'time': notification.created_at.isoformat(),
            'read': notification.is_read
        }, room=str(user_id))
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to create notification for user %s", user_id)

# WebSocket event for clients to connect
@socketio.on('connect_notification')
def handle_connect(data):
    token = data.get('token')
    if not token:
        logger.error("No token provided in SocketIO connection")
        disconnect()
        return

    try:
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
        logger.info("User %s connected for notifications", user_id)
        socketio.server.enter_room(request.sid, str(user_id))
    except Exception as e:
        logger.error("Invalid token in SocketIO connection: %s", str(e))
        disconnect()

# REST endpoint to list notifications
@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    pagination = (
        Notification.query
        .filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    items = [
        {
            "id": notif.id,
            "type": "System",
            "message": notif.message,
            "subMessage": notif.message,
            "time": notif.created_at.isoformat(),
            "read": notif.is_read
        }
        for notif in pagination.items
    ]
    return jsonify({
        "items": items,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }), 200

# REST endpoint to mark notification as read
@notifications_bp.route("/<int:note_id>/read", methods=["POST"])
@jwt_required()
def mark_read(note_id):
    user_id = int(get_jwt_identity())
    notification = (
        Notification.query
        .filter_by(id=note_id, user_id=user_id)
        .first_or_404()
    )
    if notification.is_read:
        return jsonify({"message": "Already marked as read"}), 200
    notification.is_read = True
    try:
        db.session.commit()
        logger.info("User %s marked notification %s as read", user_id, note_id)
        return jsonify({"message": "Marked as read"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to mark notification %s read for user %s", note_id, user_id)
        return jsonify({"error": "Could not mark as read"}), 500

# Add notification triggers (already present, ensuring consistency)
def notify_new_post(post):
    category_id = post.category_id
    from .models import Subscription
    subscribers = Subscription.query.filter_by(category_id=category_id).all()
    for sub in subscribers:
        message = f'New {post.type} posted in category ID {category_id}: "{post.title}"'
        create_and_emit_notification(sub.user_id, message, post.id)

def notify_new_comment(comment):
    post = comment.post
    message = f'New comment on post "{post.title}": "{comment.body}"'
    post_author_id = post.category.created_by
    if post_author_id and post_author_id != comment.user_id:
        create_and_emit_notification(post_author_id, message, post.id)

def notify_new_like(like):
    post = Post.query.get(like.post_id)
    message = f'Your post "{post.title}" received a new like!'
    post_author_id = post.category.created_by
    if post_author_id and post_author_id != like.user_id:
        create_and_emit_notification(post_author_id, message, post.id)