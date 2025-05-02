import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import Notification
logger = logging.getLogger(__name__)
notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")
@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = (
        Notification.query
        .filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    items = [
        {
            "id": n.id,
            "content_id": n.content_id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        }
        for n in pagination.items
    ]
    return jsonify({
        "items": items,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total
    }), 200
@notifications_bp.route("/<int:note_id>/read", methods=["POST"])
@jwt_required()
def mark_read(note_id):
    user_id = int(get_jwt_identity())
    note = (
        Notification.query
        .filter_by(id=note_id, user_id=user_id)
        .first_or_404()
    )
    if note.is_read:
        return jsonify({"message": "Already marked as read"}), 200
    note.is_read = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to mark notification %s read for user %s", note_id, user_id)
        return jsonify({"error": "Could not mark as read"}), 500
    logger.info("User %s marked notification %s as read", user_id, note_id)
    return jsonify({"message": "Marked as read"}), 200