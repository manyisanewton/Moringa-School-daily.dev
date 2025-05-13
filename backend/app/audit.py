import logging
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import db
from .models import AuditLog
logger = logging.getLogger(__name__)
audit_bp = Blueprint("audit", __name__, url_prefix="/audit")
@audit_bp.route("/logs", methods=["GET"])
@jwt_required()
def list_logs():
    default_limit = current_app.config.get("AUDIT_LOG_DEFAULT_LIMIT", 50)
    max_limit = current_app.config.get("AUDIT_LOG_MAX_LIMIT", 200)
    limit = request.args.get("limit", type=int)
    if limit is None:
        limit = default_limit
    else:
        limit = min(limit, max_limit)
    logs = (
        db.session
        .query(AuditLog)
        .order_by(AuditLog.id.desc())
        .limit(limit)
        .all()
    )
    out = []
    for l in logs:
        out.append({
            "user_id": l.user_id,
            "action": l.action,
            "target_type": l.target_type,
            "target_id": l.target_id,
        })
    return jsonify(out), 200
def audit(action: str, target_type: str, target_id_arg: str = None, details_fn=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            resp = fn(*args, **kwargs)
            try:
                user_id = int(get_jwt_identity())
                target_id = None
                if target_id_arg:
                    target_id = kwargs.get(target_id_arg)
                    if target_id is None:
                        payload = request.get_json(silent=True) or {}
                        target_id = payload.get(target_id_arg)
                if target_id is None:
                    target_id = user_id
                target_id = int(target_id)
                details = None
                if details_fn:
                    try:
                        details = details_fn(kwargs, resp)
                    except Exception:
                        current_app.logger.exception("Failed to run details_fn for %s", action)
                log = AuditLog(
                    user_id=user_id,
                    action=action,
                    target_type=target_type,
                    target_id=target_id,
                    details=details
                )
                db.session.add(log)
                db.session.commit()
            except Exception:
                current_app.logger.exception("Failed to record audit log for %s", action)
            return resp
        return wrapper
    return decorator