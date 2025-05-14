import logging
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import Category, Subscription
logger = logging.getLogger(__name__)
subscriptions_bp = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")
@subscriptions_bp.route("", methods=["GET"])
@jwt_required()
def list_subscriptions():
    user_id = int(get_jwt_identity())
    subs = (
        Subscription.query
        .filter_by(user_id=user_id)
        .join(Category)
        .all()
    )
    result = [
        {
            "category_id": s.category_id,
            "name": s.category.name,
            "description": s.category.description,
            "subscribed_at": s.created_at.isoformat()
        }
        for s in subs
    ]
    return jsonify(result), 200
@subscriptions_bp.route("/<int:category_id>", methods=["POST"])
@jwt_required()
def subscribe(category_id):
    user_id = int(get_jwt_identity())
    category = Category.query.get_or_404(category_id)
    if Subscription.query.filter_by(user_id=user_id, category_id=category_id).first():
        return jsonify({"error": "Already subscribed"}), 400
    sub = Subscription(user_id=user_id, category_id=category_id)
    db.session.add(sub)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(
            "Failed to subscribe user %s to category %s",
            user_id, category_id
        )
        return jsonify({"error": "Subscription failed"}), 500
    return jsonify({"message": f"Subscribed to '{category.name}'"}), 201
@subscriptions_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
def unsubscribe(category_id):
    user_id = int(get_jwt_identity())
    sub = Subscription.query.filter_by(
        user_id=user_id, category_id=category_id
    ).first()
    if not sub:
        abort(404, description="Not subscribed to this category")
    db.session.delete(sub)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(
            "Failed to unsubscribe user %s from category %s",
            user_id, category_id
        )
        return jsonify({"error": "Unsubscription failed"}), 500
    return jsonify({"message": "Unsubscribed successfully"}), 200