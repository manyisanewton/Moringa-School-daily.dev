import logging
import requests
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import Schema, ValidationError, fields, validate, EXCLUDE
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import event
from . import db
from .models import Category, Post, Like
from .utils import roles_required
from .notifications import notify_new_post, notify_new_like

logger = logging.getLogger(__name__)
categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

RSS2JSON_API_KEY = 'qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz'
VIDEO_API = f"https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id=UC8butISFwT-Wl7EV0hUK0BQ&api_key={RSS2JSON_API_KEY}"
ARTICLE_API = 'https://dev.to/api/articles'
AUDIO_API = f"https://listen-api.listennotes.com/api/v2/search?q=podcast&sort_by_date=0&type=episode&offset=0&len_min=10&len_max=30&genre_ids=68,69&published_before=1698777600&published_after=1368902400&only_in=title%2Cdescription&language=English&safe_mode=0"
LISTENNOTES_API_KEY = '7414408b9ba6479aba86eb06545f7a98'
DEVTO_API_KEY = 'your-devto-api-key'

class CategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE
    name = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    description = fields.Str(allow_none=True, load_default=None, validate=validate.Length(max=256))

@categories_bp.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError):
    return jsonify({"errors": err.messages}), 400

# Event listener to seed hardcoded categories on app startup
@event.listens_for(Category.__table__, "after_create")
def seed_categories(target, connection, **kw):
    from flask import current_app
    if current_app and current_app.config.get("TESTING"):
        return
    count = connection.execute("SELECT COUNT(*) FROM categories").scalar()
    if count == 0:
        hardcoded_categories = [
            {"name": "Fullstack Development", "description": "Content related to fullstack development."},
            {"name": "Cyber Security", "description": "Content related to cybersecurity practices."},
            {"name": "Data Science", "description": "Content related to data science and analytics."},
            {"name": "Mobile Development", "description": "Content related to mobile app development."},
            {"name": "Artificial Intelligence", "description": "Content related to AI and machine learning."}
        ]
        for cat in hardcoded_categories:
            connection.execute(
                target.insert().values(name=cat["name"], description=cat["description"], created_by=1)  # Assuming user_id 1 as creator
            )

@categories_bp.route("", methods=["GET"])
def list_categories():
    cats = Category.query.order_by(Category.name).all()
    result = []
    for c in cats:
        posts = Post.query.filter_by(category_id=c.id).limit(5).all()
        result.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "posts": [{
                "id": p.id,
                "type": p.type,
                "title": p.title,
                "author": p.author,
                "date": p.date.isoformat(),
                "likes": p.likes,
                "comments": p.comments
            } for p in posts]
        })
    return jsonify(result), 200

@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    c = Category.query.get_or_404(category_id)
    posts = Post.query.filter_by(category_id=c.id).limit(5).all()
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "posts": [{
            "id": p.id,
            "type": p.type,
            "title": p.title,
            "author": p.author,
            "date": p.date.isoformat(),
            "likes": p.likes,
            "comments": p.comments
        } for p in posts]
    }), 200

@categories_bp.route("", methods=["POST"])
@jwt_required()
@roles_required("Admin", "TechWriter")
def create_category():
    data = CategorySchema().load(request.get_json() or {})
    if Category.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Category name already exists."}), 409
    c = Category(
        name=data["name"],
        description=data["description"],
        created_by=int(get_jwt_identity()),
    )
    db.session.add(c)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("create_category failed")
        return jsonify({"error": "Category creation failed."}), 500
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
    }), 201

@categories_bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
@roles_required("Admin", "TechWriter")
def update_category(category_id):
    c = Category.query.get_or_404(category_id)
    data = CategorySchema(partial=True).load(request.get_json() or {})
    if "name" not in data:
        return jsonify({"errors": {"name": ["Missing data for required field."]}}), 400
    if (
        data["name"] != c.name
        and Category.query.filter(Category.name == data["name"], Category.id != category_id).first()
    ):
        return jsonify({"error": "Category name already exists."}), 409
    c.name = data["name"]
    if "description" in data:
        c.description = data["description"]
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("update_category failed")
        return jsonify({"error": "Category update failed."}), 500
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
    }), 200

@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin", "TechWriter")
def delete_category(category_id):
    c = Category.query.get_or_404(category_id)
    db.session.delete(c)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("delete_category failed")
        return jsonify({"error": "Category deletion failed."}), 500
    return jsonify({"message": "Category deleted."}), 200

@categories_bp.route("/fetch-external-data", methods=["GET"])
def fetch_external_data():
    try:
        video_response = requests.get(VIDEO_API)
        video_response.raise_for_status()
        article_response = requests.get(ARTICLE_API, headers={'api-key': DEVTO_API_KEY})
        article_response.raise_for_status()
        audio_response = requests.get(AUDIO_API, headers={'X-ListenAPI-Key': LISTENNOTES_API_KEY})
        audio_response.raise_for_status()

        videos = video_response.json().get('items', [])
        articles = article_response.json()
        audios = audio_response.json().get('results', [])

        category_data = [
            {
                "id": 1,
                "name": "Fullstack Development",
                "posts": [
                    {"id": index + 1, "type": "video", "title": item['title'], "author": item.get('author', 'Unknown'), "date": item['pubDate'], "url": item.get('link', ''), "likes": 0, "comments": 0}
                    for index, item in enumerate(videos[:3])
                ] + [
                    {"id": len(videos) + index + 1, "type": "article", "title": item['title'], "author": item.get('user', {}).get('name', 'Unknown'), "date": item['published_at'], "url": '', "likes": item.get('positive_reactions_count', 0), "comments": 0}
                    for index, item in enumerate(articles[:2])
                ]
            },
            {
                "id": 2,
                "name": "Cyber Security",
                "posts": [
                    {"id": index + 1, "type": "audio", "title": item['title'], "author": item.get('publisher', 'Unknown'), "date": item['published_date'], "url": item.get('audio', ''), "likes": 0, "comments": 0}
                    for index, item in enumerate(audios[:3])
                ] + [
                    {"id": len(audios) + index + 1, "type": "article", "title": item['title'], "author": item.get('user', {}).get('name', 'Unknown'), "date": item['published_at'], "url": '', "likes": item.get('positive_reactions_count', 0), "comments": 0}
                    for index, item in enumerate(articles[2:4])
                ]
            },
        ]

        # Save posts to database and notify users
        for cat_data in category_data:
            category = Category.query.get(cat_data["id"])
            if not category:
                category = Category(id=cat_data["id"], name=cat_data["name"], created_by=1)  # Assuming user_id 1
                db.session.add(category)
                db.session.commit()
            for post_data in cat_data["posts"]:
                post = Post(
                    category_id=category.id,
                    type=post_data["type"],
                    title=post_data["title"],
                    author=post_data["author"],
                    date=post_data["date"],
                    likes=post_data["likes"],
                    comments=post_data["comments"]
                )
                db.session.add(post)
                db.session.commit()
                notify_new_post(post)  # Trigger notification for new post

        return jsonify(category_data), 200
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to fetch external data: %s", str(e))
        return jsonify({"error": "Failed to fetch external data."}), 500

@categories_bp.route("/<int:post_id>/like", methods=["POST"])
@jwt_required()
def like_post(post_id):
    user_id = int(get_jwt_identity())
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    like = Like(user_id=user_id, post_id=post_id)
    db.session.add(like)
    try:
        db.session.commit()
        post.likes = Like.query.filter_by(post_id=post_id).count()
        db.session.commit()
        notify_new_like(like)  # Trigger notification for new like
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Failed to like post %s by user %s", post_id, user_id)
        return jsonify({"error": "Could not like post"}), 500
    
    return jsonify({"message": "Post liked", "likes": post.likes}), 200

@categories_bp.route("/<int:post_id>/likes", methods=["GET"])
def get_likes(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found."}), 404

    like_count = Like.query.filter_by(post_id=post_id).count()
    return jsonify({"likes": like_count}), 200