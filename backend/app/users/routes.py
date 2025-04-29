from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..users.models import User, followers
from ..content.models import Content, Comment, Like
from ..categories.models import Category
from ..notifications.models import Notification
from ..notifications.routes import create_notification
from datetime import datetime, timedelta

users_bp = Blueprint('users', __name__)

# Update user profile
@users_bp.route('/api/users/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    current_user = User.query.get(get_jwt_identity())
    data = ramoquest.get_json()
    current_user.profile = data
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

# Update category subscriptions
@users_bp.route('/api/users/subscriptions', methods=['PUT'])
@jwt_required()
def update_subscriptions():
    current_user = User.query.get(get_jwt_identity())
    data = request.get_json()
    category_ids = data.get('category_ids', [])
    valid_categories = Category.query.filter(Category.id.in_(category_ids)).all()
    if len(valid_categories) != len(category_ids):
        return jsonify({'message': 'Invalid category IDs'}), 400
    current_user.subscriptions = category_ids
    db.session.commit()
    return jsonify({'message': 'Subscriptions updated successfully'}), 200

# Create content (triggers notifications for subscribers)
@users_bp.route('/api/users/content', methods=['POST'])
@jwt_required()
def user_create_content():
    current_user = User.query.get(get_jwt_identity())
    data = request.get_json()
    content = Content(
        title=data['title'],
        body=data['body'],
        content_type=data['content_type'],
        category_id=data['category_id'],
        author_id=current_user.id
    )
    db.session.add(content)
    db.session.flush()  # Ensure content.id is available

    # Notify users subscribed to this category
    subscribed_users = User.query.filter(User.subscriptions.contains([data['category_id']])).all()
    for user in subscribed_users:
        if user.id != current_user.id:  # Don't notify the author
            create_notification(
                user_id=user.id,
                message=f"New content posted in your subscribed category: {content.title}",
                content_id=content.id,
                notification_type='new_content'
            )

    db.session.commit()
    return jsonify({'message': 'Content created successfully', 'content_id': content.id}), 201

# Read content (increment views)
@users_bp.route('/api/users/content/<content_id>', methods=['GET'])
@jwt_required()
def read_content(content_id):
    content = Content.query.get_or_404(content_id)
    if not content.is_approved or content.is_flagged:
        return jsonify({'message': 'Content not available'}), 403
    # Increment views
    content.views += 1
    db.session.commit()
    return jsonify({
        'id': content.id,
        'title': content.title,
        'body': content.body,
        'content_type': content.content_type,
        'category_id': content.category_id,
        'author_id': content.author_id,
        'created_at': content.created_at.isoformat(),
        'views': content.views
    }), 200

# Create comment (triggers notification for content author)
@users_bp.route('/api/users/content/<content_id>/comment', methods=['POST'])
@jwt_required()
def create_comment(content_id):
    current_user = User.query.get(get_jwt_identity())
    content = Content.query.get_or_404(content_id)
    data = request.get_json()
    parent_comment_id = data.get('parent_comment_id')
    if parent_comment_id:
        parent_comment = Comment.query.get_or_404(parent_comment_id)
        if parent_comment.content_id != content_id:
            return jsonify({'message': 'Invalid parent comment'}), 400
    comment = Comment(
        content_id=content_id,
        user_id=current_user.id,
        body=data['body'],
        parent_comment_id=parent_comment_id
    )
    db.session.add(comment)
    db.session.flush()  # Ensure comment.id is available

    # Notify content author about the new comment
    if content.author_id != current_user.id:
        create_notification(
            user_id=content.author_id,
            message=f"New comment on your content '{content.title}': {comment.body[:50]}...",
            content_id=content_id,
            notification_type='comment'
        )

    db.session.commit()
    return jsonify({'message': 'Comment created successfully', 'comment_id': comment.id}), 201

# View comments (including threaded comments)
@users_bp.route('/api/users/content/<content_id>/comments', methods=['GET'])
@jwt_required()
def view_comments(content_id):
    Content.query.get_or_404(content_id)  # Ensure content exists
    comments = Comment.query.filter_by(content_id=content_id).all()
    def build_comment_tree(comment_list, parent_id=None):
        tree = []
        for comment in comment_list:
            if comment.parent_comment_id == parent_id:
                children = build_comment_tree(comment_list, comment.id)
                tree.append({
                    'id': comment.id,
                    'body': comment.body,
                    'user_id': comment.user_id,
                    'created_at': comment.created_at.isoformat(),
                    'children': children
                })
        return tree
    comment_tree = build_comment_tree(comments)
    return jsonify(comment_tree), 200

# Like/Dislike content (triggers notification for content author)
@users_bp.route('/api/users/content/<content_id>/like', methods=['POST'])
@jwt_required()
def like_content(content_id):
    current_user = User.query.get(get_jwt_identity())
    content = Content.query.get_or_404(content_id)
    data = request.get_json()
    existing_like = Like.query.filter_by(user_id=current_user.id, content_id=content_id).first()
    if existing_like:
        existing_like.is_like = data['is_like']
    else:
        like = Like(
            content_id=content_id,
            user_id=current_user.id,
            is_like=data['is_like']
        )
        db.session.add(like)

    if content.author_id != current_user.id:
        action = "liked" if data['is_like'] else "disliked"
        create_notification(
            user_id=content.author_id,
            message=f"Your content '{content.title}' was {action} by another user",
            content_id=content_id,
            notification_type='like'
        )

    db.session.commit()
    return jsonify({'message': 'Like/Dislike recorded successfully'}), 201

# Update wishlist
@users_bp.route('/api/users/wishlist', methods=['PUT'])
@jwt_required()
def update_wishlist():
    current_user = User.query.get(get_jwt_identity())
    data = request.get_json()
    content_ids = data.get('content_ids', [])
    valid_content = Content.query.filter(Content.id.in_(content_ids)).all()
    if len(valid_content) != len(content_ids):
        return jsonify({'message': 'Invalid content IDs'}), 400
    current_user.wishlist = content_ids
    db.session.commit()
    return jsonify({'message': 'Wishlist updated successfully'}), 200

# Share/recommend content
@users_bp.route('/api/users/content/<content_id>/share', methods=['POST'])
@jwt_required()
def share_content(content_id):
    Content.query.get_or_404(content_id)  # Ensure content exists
    return jsonify({'message': 'Content shared successfully'}), 200

# Get recommendations
@users_bp.route('/api/users/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    current_user = User.query.get(get_jwt_identity())
    recommendations = Content.query.filter(
        Content.category_id.in_(current_user.subscriptions),
        Content.is_approved == True,
        Content.is_flagged == False
    ).order_by(Content.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'category_id': c.category_id,
        'content_type': c.content_type
    } for c in recommendations]), 200

# Get user activity feed
@users_bp.route('/api/users/activity', methods=['GET'])
@jwt_required()
def get_user_activity():
    current_user = User.query.get(get_jwt_identity())
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Fetch recent activities (content posted, comments made, likes given)
    activities = []

    # Content posted
    contents = Content.query.filter_by(author_id=current_user.id).order_by(Content.created_at.desc()).limit(50).all()
    activities.extend([{
        'type': 'content',
        'action': 'posted',
        'title': content.title,
        'content_id': content.id,
        'timestamp': content.created_at.isoformat()
    } for content in contents])

    # Comments made
    comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.created_at.desc()).limit(50).all()
    activities.extend([{
        'type': 'comment',
        'action': 'commented',
        'body': comment.body[:50] + '...' if len(comment.body) > 50 else comment.body,
        'content_id': comment.content_id,
        'timestamp': comment.created_at.isoformat()
    } for comment in comments])

    # Likes given
    likes = Like.query.filter_by(user_id=current_user.id).order_by(Like.id.desc()).limit(50).all()
    activities.extend([{
        'type': 'like',
        'action': 'liked' if like.is_like else 'disliked',
        'content_id': like.content_id,
        'timestamp': like.id  # Using ID as a proxy for timestamp
    } for like in likes])

    # Sort activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    # Paginate
    total = len(activities)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_activities = activities[start:end]

    return jsonify({
        'activities': paginated_activities,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    }), 200

# Follow a user
@users_bp.route('/api/users/follow/<user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user = User.query.get(get_jwt_identity())
    user_to_follow = User.query.get_or_404(user_id)
    if user_to_follow == current_user:
        return jsonify({'message': 'Cannot follow yourself'}), 400
    if user_to_follow in current_user.following:
        return jsonify({'message': 'Already following this user'}), 400
    current_user.following.append(user_to_follow)
    db.session.commit()
    create_notification(
        user_id=user_to_follow.id,
        message=f"{current_user.username} started following you",
        notification_type='follow'
    )
    return jsonify({'message': f'Now following {user_to_follow.username}'}), 200

# Unfollow a user
@users_bp.route('/api/users/unfollow/<user_id>', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user = User.query.get(get_jwt_identity())
    user_to_unfollow = User.query.get_or_404(user_id)
    if user_to_unfollow == current_user:
        return jsonify({'message': 'Cannot unfollow yourself'}), 400
    if user_to_unfollow not in current_user.following:
        return jsonify({'message': 'Not following this user'}), 400
    current_user.following.remove(user_to_unfollow)
    db.session.commit()
    return jsonify({'message': f'Unfollowed {user_to_unfollow.username}'}), 200

# Get followed users' content feed
@users_bp.route('/api/users/followed-content', methods=['GET'])
@jwt_required()
def get_followed_content():
    current_user = User.query.get(get_jwt_identity())
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    followed_ids = [user.id for user in current_user.following]
    pagination = Content.query.filter(
        Content.author_id.in_(followed_ids),
        Content.is_approved == True,
        Content.is_flagged == False
    ).order_by(Content.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    contents = pagination.items
    return jsonify({
        'contents': [{
            'id': c.id,
            'title': c.title,
            'category_id': c.category_id,
            'content_type': c.content_type,
            'author_id': c.author_id,
            'created_at': c.created_at.isoformat()
        } for c in contents],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

# Get user profile statistics
@users_bp.route('/api/users/stats/<user_id>', methods=['GET'])
@jwt_required()
def get_user_stats(user_id):
    user = User.query.get_or_404(user_id)
    posts_count = Content.query.filter_by(author_id=user.id).count()
    likes_received = Like.query.join(Content).filter(Content.author_id == user.id, Like.is_like == True).count()
    followers_count = user.followers.count()
    following_count = user.following.count()
    return jsonify({
        'username': user.username,
        'posts_count': posts_count,
        'likes_received': likes_received,
        'followers_count': followers_count,
        'following_count': following_count
    }), 200

# Search users
@users_bp.route('/api/users/search', methods=['GET'])
@jwt_required()
def search_users():
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    pagination = User.query.filter(
        User.username.ilike(f'%{query}%'),
        User.is_active == True
    ).paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'role': user.role
        } for user in users],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

# Get content engagement analytics
@users_bp.route('/api/users/content/<content_id>/analytics', methods=['GET'])
@jwt_required()
def get_content_analytics(content_id):
    current_user = User.query.get(get_jwt_identity())
    content = Content.query.get_or_404(content_id)
    if content.author_id != current_user.id:
        return jsonify({'message': 'Can only view analytics for your own content'}), 403
    likes_count = Like.query.filter_by(content_id=content_id, is_like=True).count()
    dislikes_count = Like.query.filter_by(content_id=content_id, is_like=False).count()
    comments_count = Comment.query.filter_by(content_id=content_id).count()
    return jsonify({
        'content_id': content.id,
        'title': content.title,
        'views': content.views,
        'likes': likes_count,
        'dislikes': dislikes_count,
        'comments': comments_count
    }), 200

# Get notifications (moved to notifications/routes.py)
@users_bp.route('/api/users/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user = User.query.get(get_jwt_identity())
    new_content = Content.query.filter(
        Content.category_id.in_(current_user.subscriptions),
        Content.is_approved == True,
        Content.is_flagged == False,
        Content.created_at > datetime.utcnow() - timedelta(days=1)
    ).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'category_id': c.category_id,
        'content_type': c.content_type
    } for c in new_content]), 200