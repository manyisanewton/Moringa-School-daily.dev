import logging
from flask import Blueprint, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import Wishlist, Content
logger = logging.getLogger(__name__)
wishlists_bp = Blueprint(
    "wishlists",
    __name__,
    url_prefix="/wishlists"
)
@wishlists_bp.errorhandler(404)
def not_found(err):
    message = err.description or "Not found"
    return jsonify(error=message), 404
@wishlists_bp.route("", methods=["GET"])
@jwt_required()
def list_wishlists():
    user_id = int(get_jwt_identity())
    items = Wishlist.query.filter_by(user_id=user_id).all()
    result = [
        {
            "id": w.id,
            "content_id": w.content_id,
            "title": w.content.title,
            "added_at": w.created_at.isoformat(),
        }
        for w in items
    ]
    return jsonify(result), 200
@wishlists_bp.route("/<content_id>", methods=["POST"])
@jwt_required()
def add_to_wishlist(content_id):
    user_id = int(get_jwt_identity())
    try:
        cid = int(content_id)
    except ValueError:
        abort(404, description="Content not found")
    Content.query.get_or_404(cid, description="Content not found")
    if Wishlist.query.filter_by(user_id=user_id, content_id=cid).first():
        return jsonify(error="Already in wishlist"), 400
    w = Wishlist(user_id=user_id, content_id=cid)
    db.session.add(w)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(
            "Failed to add content %s to wishlist for user %s", cid, user_id
        )
        return jsonify(error="Could not add to wishlist"), 500
    return jsonify(message="Added to wishlist", id=w.id), 201
@wishlists_bp.route("/<content_id>", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist(content_id):
    user_id = int(get_jwt_identity())
    try:
        cid = int(content_id)
    except ValueError:
        abort(404, description="Not in wishlist")
    w = Wishlist.query.filter_by(user_id=user_id, content_id=cid).first()
    if not w:
        abort(404, description="Not in wishlist")
    db.session.delete(w)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(
            "Failed to remove content %s from wishlist for user %s", cid, user_id
        )
        return jsonify(error="Could not remove from wishlist"), 500
    return jsonify(message="Removed from wishlist"), 200