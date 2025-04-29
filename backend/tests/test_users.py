import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from ..app import db
from ..app.users.models import User
from ..app.content.models import Content, Comment, Like
from ..app.categories.models import Category
from ..app.notifications.models import Notification
from ..app.users.routes import users_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    db.init_app(app)
    app.register_blueprint(users_bp, url_prefix='/api/users')
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_db(app):
    with app.app_context():
        # Create test users
        user = User(
            username='testuser',
            email='test@example.com',
            password='hashedpassword',
            role='user'
        )
        db.session.add(user)
        user2 = User(
            username='testuser2',
            email='test2@example.com',
            password='hashedpassword2',
            role='user'
        )
        db.session.add(user2)
        # Create a test category
        category = Category(name='TestCategory')
        db.session.add(category)
        # Create test content
        content = Content(
            title='Test Content',
            body='This is a test',
            content_type='article',
            category_id=category.id,
            author_id=user.id,
            is_approved=True,
            is_flagged=False
        )
        db.session.add(content)
        db.session.commit()
        # Subscribe user2 to the category
        user2.subscriptions = [category.id]
        db.session.commit()
        return user.id, user2.id, category.id, content.id

def test_update_user_profile(client, init_db):
    user_id, _, _, _ = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.put('/api/users/profile', 
                         json={'bio': 'Test bio'},
                         headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Profile updated successfully'

def test_update_subscriptions(client, init_db):
    user_id, _, category_id, _ = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.put('/api/users/subscriptions',
                         json={'category_ids': [category_id]},
                         headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Subscriptions updated successfully'

def test_create_content_with_notification(client, init_db):
    user_id, user2_id, category_id, _ = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/users/content',
                          json={
                              'title': 'New Content',
                              'body': 'This is new content',
                              'content_type': 'article',
                              'category_id': category_id
                          },
                          headers=headers)
    assert response.status_code == 201
    assert response.json['message'] == 'Content created successfully'
    notification = Notification.query.filter_by(user_id=user2_id).first()
    assert notification is not None
    assert "New content posted" in notification.message

def test_read_content_with_views(client, init_db):
    user_id, _, _, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get(f'/api/users/content/{content_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['title'] == 'Test Content'
    assert response.json['views'] == 1  # Views incremented

def test_create_comment_with_notification(client, init_db):
    user_id, user2_id, _, content_id = init_db
    token = create_access_token(identity=user2_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post(f'/api/users/content/{content_id}/comment',
                          json={'body': 'Great content!'},
                          headers=headers)
    assert response.status_code == 201
    assert response.json['message'] == 'Comment created successfully'
    notification = Notification.query.filter_by(user_id=user_id).first()
    assert notification is not None
    assert "New comment on your content" in notification.message

def test_view_comments(client, init_db):
    user_id, _, _, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    client.post(f'/api/users/content/{content_id}/comment',
                json={'body': 'Great content!'},
                headers=headers)
    response = client.get(f'/api/users/content/{content_id}/comments',
                         headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['body'] == 'Great content!'

def test_like_content_with_notification(client, init_db):
    user_id, user2_id, _, content_id = init_db
    token = create_access_token(identity=user2_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post(f'/api/users/content/{content_id}/like',
                          json={'is_like': True},
                          headers=headers)
    assert response.status_code == 201
    assert response.json['message'] == 'Like/Dislike recorded successfully'
    notification = Notification.query.filter_by(user_id=user_id).first()
    assert notification is not None
    assert "Your content 'Test Content' was liked" in notification.message

def test_update_wishlist(client, init_db):
    user_id, _, _, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.put('/api/users/wishlist',
                         json={'content_ids': [content_id]},
                         headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Wishlist updated successfully'

def test_share_content(client, init_db):
    user_id, _, _, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post(f'/api/users/content/{content_id}/share',
                          headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Content shared successfully'

def test_get_recommendations(client, init_db):
    user_id, _, category_id, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    client.put('/api/users/subscriptions',
              json={'category_ids': [category_id]},
              headers=headers)
    response = client.get('/api/users/recommendations',
                         headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == content_id

def test_get_user_activity(client, init_db):
    user_id, _, category_id, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    # Add a comment and like to create activity
    client.post(f'/api/users/content/{content_id}/comment',
                json={'body': 'Great content!'},
                headers=headers)
    client.post(f'/api/users/content/{content_id}/like',
                json={'is_like': True},
                headers=headers)
    response = client.get('/api/users/activity?page=1&per_page=10', headers=headers)
    assert response.status_code == 200
    assert len(response.json['activities']) >= 2  # Content, comment, like
    assert response.json['total'] >= 2
    assert any(activity['type'] == 'content' for activity in response.json['activities'])
    assert any(activity['type'] == 'comment' for activity in response.json['activities'])
    assert any(activity['type'] == 'like' for activity in response.json['activities'])

def test_follow_unfollow_user(client, init_db):
    user_id, user2_id, _, _ = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    # Follow user2
    response = client.post(f'/api/users/follow/{user2_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Now following testuser2'
    # Check notification
    notification = Notification.query.filter_by(user_id=user2_id).first()
    assert notification is not None
    assert "started following you" in notification.message
    # Unfollow user2
    response = client.post(f'/api/users/unfollow/{user2_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Unfollowed testuser2'

def test_get_followed_content(client, init_db):
    user_id, user2_id, _, _ = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    # Follow user2
    client.post(f'/api/users/follow/{user2_id}', headers=headers)
    # Create content by user2
    token2 = create_access_token(identity=user2_id)
    headers2 = {'Authorization': f'Bearer {token2}'}
    client.post('/api/users/content',
                json={
                    'title': 'User2 Content',
                    'body': 'Content by user2',
                    'content_type': 'article',
                    'category_id': init_db()[2]
                },
                headers=headers2)
    response = client.get('/api/users/followed-content?page=1&per_page=10', headers=headers)
    assert response.status_code == 200
    assert len(response.json['contents']) == 1
    assert response.json['contents'][0]['title'] == 'User2 Content'

def test_get_user_stats(client, init_db):
    user_id, user2_id, _, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    # Follow user1
    token2 = create_access_token(identity=user2_id)
    headers2 = {'Authorization': f'Bearer {token2}'}
    client.post(f'/api/users/follow/{user_id}', headers=headers2)
    # Like user1's content
    client.post(f'/api/users/content/{content_id}/like',
                json={'is_like': True},
                headers=headers2)
    response = client.get(f'/api/users/stats/{user_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['posts_count'] == 1
    assert response.json['likes_received'] == 1
    assert response.json['followers_count'] == 1
    assert response.json['following_count'] == 0

def test_search_users(client, init_db):
    user_id, user2_id, _, _ = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/users/search?query=testuser&page=1&per_page=10', headers=headers)
    assert response.status_code == 200
    assert len(response.json['users']) == 2
    assert response.json['total'] == 2
    assert any(user['username'] == 'testuser' for user in response.json['users'])
    assert any(user['username'] == 'testuser2' for user in response.json['users'])

def test_get_content_analytics(client, init_db):
    user_id, _, _, content_id = init_db
    token = create_access_token(identity=user_id)
    headers = {'Authorization': f'Bearer {token}'}
    # Add a view, like, and comment
    client.get(f'/api/users/content/{content_id}', headers=headers)
    client.post(f'/api/users/content/{content_id}/like',
                json={'is_like': True},
                headers=headers)
    client.post(f'/api/users/content/{content_id}/comment',
                json={'body': 'Great content!'},
                headers=headers)
    response = client.get(f'/api/users/content/{content_id}/analytics', headers=headers)
    assert response.status_code == 200
    assert response.json['views'] == 1
    assert response.json['likes'] == 1
    assert response.json['dislikes'] == 0
    assert response.json['comments'] == 1