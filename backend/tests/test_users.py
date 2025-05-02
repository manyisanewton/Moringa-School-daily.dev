import pytest
from flask import url_for
from unittest.mock import patch
from app.models import User, Role, UserProfile, UserRole
from app import db

@pytest.fixture
def user(client, db_session):
    user = User(email='test@example.com', is_active=True)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def token(user):
    from flask_jwt_extended import create_access_token
    return create_access_token(identity=user.id)

@pytest.fixture
def headers(token):
    return {'Authorization': f'Bearer {token}'}

def test_get_my_profile_creates_profile_if_not_exists(client, user, headers):
    res = client.get('/users/me/profile', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data['email'] == user.email
    assert 'name' in data

def test_update_my_profile(client, user, headers):
    payload = {
        'name': 'Updated Name',
        'bio': 'Bio info',
        'avatar_url': 'http://example.com/avatar.jpg',
        'social_links': 'https://twitter.com/user'
    }
    res = client.put('/users/me/profile', headers=headers, json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['name'] == payload['name']
    assert data['bio'] == payload['bio']

@patch('app.routes.users.roles_required', lambda role: lambda fn: fn)  # Bypass @roles_required
def test_promote_user_success(client, headers, db_session):
    admin = User(email='admin@example.com', is_active=True)
    user = User(email='normal@example.com', is_active=True)
    role = Role(name='Admin')
    db_session.add_all([admin, user, role])
    db_session.commit()

    # Add admin role to the admin user
    db_session.add(UserRole(user_id=admin.id, role_id=role.id))
    db_session.commit()

    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=admin.id)
    res = client.post(
        f'/users/{user.id}/promote/Admin',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert f'promoted to Admin' in data['message']

def test_update_profile_validation_error(client, headers):
    payload = {
        'avatar_url': 'not-a-valid-url'
    }
    res = client.put('/users/me/profile', headers=headers, json=payload)
    assert res.status_code == 400
    assert 'errors' in res.get_json()
