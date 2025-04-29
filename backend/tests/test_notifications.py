import pytest
from app import create_app
from app.extensions import db
from app.models.notification import Notification

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_notification(client):
    res = client.post('/api/notifications/create', json={
        'user_id': 1,
        'message': 'Test notification'
    })

    assert res.status_code == 201
    data = res.get_json()
    assert data['user_id'] == 1
    assert data['message'] == 'Test notification'
    assert data['is_read'] == False

def test_get_user_notifications(client):
    # Create notifications first
    client.post('/api/notifications/create', json={'user_id': 2, 'message': 'Notification 1'})
    client.post('/api/notifications/create', json={'user_id': 2, 'message': 'Notification 2'})

    res = client.get('/api/notifications/2')

    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2

def test_mark_as_read(client):
    res = client.post('/api/notifications/create', json={'user_id': 3, 'message': 'Read me'})
    notification_id = res.get_json()['id']

    res = client.put(f'/api/notifications/mark-read/{notification_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['is_read'] == True
