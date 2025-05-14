import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import Content, Reaction, ReactionTypeEnum
logger = logging.getLogger(__name__)
reactions_bp = Blueprint("reactions", __name__, url_prefix="/content")
@reactions_bp.route("/<int:content_id>/reactions", methods=["GET"])
def list_reactions(content_id):
    Content.query.filter_by(id=content_id).first_or_404()
    rows = (
        db.session.query(Reaction.type, func.count(Reaction.id))
        .filter_by(content_id=content_id)
        .group_by(Reaction.type)
        .all()
    )
    result = {rtype.value: count for rtype, count in rows}
    return jsonify(result), 200
@reactions_bp.route("/<int:content_id>/reactions", methods=["POST"])
@jwt_required()
def create_reaction(content_id):
    user_id = int(get_jwt_identity())
    Content.query.filter_by(id=content_id).first_or_404()
    data = request.get_json(silent=True) or {}
    rtype = data.get("type")
    valid_types = {e.value for e in ReactionTypeEnum}
    if rtype not in valid_types:
        return jsonify(error="Invalid reaction type"), 400
    if Reaction.query.filter_by(user_id=user_id, content_id=content_id).first():
        return jsonify(error="Already reacted"), 400
    try:
        reaction = Reaction(
            user_id=user_id,
            content_id=content_id,
            type=ReactionTypeEnum(rtype),
        )
        db.session.add(reaction)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(
            "Failed to create reaction for content=%s user=%s",
            content_id,
            user_id,
        )
        return jsonify(error="Could not create reaction"), 500
    return jsonify(id=reaction.id, message="Reaction created"), 201
@reactions_bp.route("/<int:content_id>/reactions", methods=["DELETE"])
@jwt_required()
def delete_reaction(content_id):
    user_id = int(get_jwt_identity())
    reaction = Reaction.query.filter_by(
        user_id=user_id,
        content_id=content_id,
    ).first()
    if not reaction:
        return jsonify(error="No reaction to delete"), 404
    try:
        db.session.delete(reaction)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(
            "Failed to delete reaction for content=%s user=%s",
            content_id,
            user_id,
        )
        return jsonify(error="Could not delete reaction"), 500
    return jsonify(message="Reaction removed"), 200