import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from werkzeug.exceptions import BadRequest
from . import db
from .models import(
    Content,
    Subscription,
    Reaction,
    ReactionTypeEnum,
    ContentStatusEnum,
)
logger = logging.getLogger(__name__)
recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/recommendations")
def _fetch_recommendations(user_id: int, page: int, per_page: int):
    subs = Subscription.query.all()
    category_ids = [s.category_id for s in subs]
    base_q = Content.query.filter(Content.status == ContentStatusEnum.Published)
    if category_ids:
        base_q = base_q.filter(Content.category_id.in_(category_ids))
    likes_sq = (
        db.session.query(
            Reaction.content_id,
            func.count(Reaction.id).label("like_count")
        )
        .filter(Reaction.type == ReactionTypeEnum.like)
        .group_by(Reaction.content_id)
        .subquery()
    )
    q = (
        base_q
        .outerjoin(likes_sq, Content.id == likes_sq.c.content_id)
        .add_columns(likes_sq.c.like_count)
        .order_by(
            likes_sq.c.like_count.desc().nullslast(),
            Content.created_at.desc()
        )
    )
    return q.paginate(page=page, per_page=per_page, error_out=False)
@recommendations_bp.route("", methods=["GET"])
@jwt_required()
def get_recommendations():
    db.session.expire_all()
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        raise BadRequest("Invalid user")
    page_param = request.args.get("page")
    if page_param is not None:
        try:
            page = int(page_param)
            assert page > 0
        except (ValueError, AssertionError):
            return jsonify(error="Invalid page parameter"), 400
    else:
        page = 1
    per_page_param = request.args.get("per_page")
    if per_page_param is not None:
        try:
            per_page = int(per_page_param)
            assert per_page > 0
        except (ValueError, AssertionError):
            return jsonify(error="Invalid per_page parameter"), 400
    else:
        per_page = current_app.config["RECOMMEND_PER_PAGE"]
    max_pp = current_app.config["MAX_RECOMMEND_PER_PAGE"]
    per_page = min(per_page, max_pp)
    try:
        pagination = _fetch_recommendations(user_id, page, per_page)
    except BadRequest as e:
        return jsonify(error=str(e)), 400
    except Exception:
        logger.exception("Unexpected error fetching recommendations for user %s", user_id)
        return jsonify(error="Failed to fetch recommendations"), 500
    items = []
    for content, like_count in pagination.items:
        body = content.body or ""
        excerpt = body if len(body) <= 200 else body[:200] + "..."
        items.append({
            "id": content.id,
            "title": content.title,
            "content_type": content.content_type.value,
            "excerpt": excerpt,
            "media_url": content.media_url,
            "category_id": content.category_id,
            "created_at": content.created_at.isoformat(),
            "like_count": int(like_count or 0),
        })
    return jsonify({
        "items": items,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }), 200