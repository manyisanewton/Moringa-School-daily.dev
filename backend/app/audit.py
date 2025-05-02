import logging
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import AuditLog
logger = logging.getLogger(__name__)
audit_bp = Blueprint("audit", __name__, url_prefix="/audit")
def record_action(action, target_type=None, target_id=None, details=None):
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        user_id = None
    entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details or {}
    )
    db.session.add(entry)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to write audit log")
def audit(action, target_type=None, target_id_arg=None, details_fn=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            result = f(*args, **kwargs)
            tid = None
            if target_id_arg:
                if target_id_arg in kwargs:
                    tid = kwargs[target_id_arg]
                else:
                    try:
                        tid = getattr(result, "json", {}) .get(target_id_arg)
                    except Exception:
                        tid = None
            det = {}
            if details_fn:
                try:
                    det = details_fn(kwargs, result) or {}
                except Exception:
                    det = {}
            record_action(action, target_type=target_type, target_id=tid, details=det)
            return result
        return wrapped
    return decorator
@audit_bp.route("/logs", methods=["GET"])
@jwt_required()
def list_logs():
    limit = min(request.args.get("limit", type=int, default=50), 200)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return jsonify([
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "target_type": l.target_type,
            "target_id": l.target_id,
            "timestamp": l.timestamp.isoformat(),
            "details": l.details
        } for l in logs
    ]), 200
