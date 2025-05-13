import pytest
from freezegun import freeze_time
from datetime import datetime, timedelta
from backend.app import db
from backend.app.models import Comment, Content, Role, User, UserRole
from backend.tests.utils import auth_header, login, register
COMMENTS_URL = "/content/{cid}/comments"
COMMENT_URL = "/content/{cid}/comments/{mid}"
EDIT_WINDOW = timedelta(minutes=30)
@pytest.fixture
def user_tokens(app):
    author_data = {
        "name": "Alice Walker",
        "email": "alice.walker@example.com",
        "password": "Fm3&Xk8!Zp4#QsT",
        "role": "User",
    }
    commenter_data = {
        "name": "Bob Carter",
        "email": "bob.carter@example.com",
        "password": "Gh7%Rt4!Ux9$VzW",
        "role": "User",
    }
    admin_data = {
        "name": "Carol Smith",
        "email": "carol.smith.admin@example.com",
        "password": "Yt4@Mk8&Nw3#LpQ",
        "role": "Admin",
    }
    client = app.test_client()
    register(client, author_data)
    register(client, commenter_data)
    register(client, admin_data)
    with app.app_context():
        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        admin_user = User.query.filter_by(email=admin_data["email"]).one()
        if not UserRole.query.filter_by(user_id=admin_user.id, role_id=admin_role.id).first():
            db.session.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
            db.session.commit()
    author_token = login(client, author_data["email"], author_data["password"])\
                   .get_json()["access_token"]
    commenter_token = login(client, commenter_data["email"], commenter_data["password"])\
                      .get_json()["access_token"]
    admin_token = login(client, admin_data["email"], admin_data["password"])\
                  .get_json()["access_token"]
    return {
        "author": (author_data, author_token),
        "commenter": (commenter_data, commenter_token),
        "admin": (admin_data, admin_token),
    }
@pytest.fixture
def sample_content(app, user_tokens):
    with app.app_context():
        author_email = user_tokens["author"][0]["email"]
        author = User.query.filter_by(email=author_email).one()
        content = Content(
            title="Test Content",
            body="Sample body",
            content_type="article",
            author_id=author.id
        )
        db.session.add(content)
        db.session.commit()
        return content.id
def test_post_and_list_comments(client, user_tokens, sample_content):
    author_token = user_tokens["author"][1]
    url = COMMENTS_URL.format(cid=sample_content)
    resp = client.post(url, json={}, headers=auth_header(author_token))
    assert resp.status_code == 400
    assert "body" in resp.get_json()["errors"]
    resp1 = client.post(url, json={"body": "Root comment"}, headers=auth_header(author_token))
    assert resp1.status_code == 201
    root_id = resp1.get_json()["id"]
    resp2 = client.post(
        url,
        json={"body": "Reply comment", "parent_id": root_id},
        headers=auth_header(author_token)
    )
    assert resp2.status_code == 201
    reply_id = resp2.get_json()["id"]
    resp3 = client.post(
        url,
        json={"body": "Orphan reply", "parent_id": 9999},
        headers=auth_header(author_token)
    )
    assert resp3.status_code == 400
    assert "Invalid parent comment" in resp3.get_data(as_text=True)
    list_resp = client.get(url)
    assert list_resp.status_code == 200
    data = list_resp.get_json()
    assert len(data) == 1
    assert data[0]["id"] == root_id
    assert len(data[0]["replies"]) == 1
    assert data[0]["replies"][0]["id"] == reply_id
def test_edit_within_and_outside_window(client, user_tokens, sample_content):
    author_data, author_token = user_tokens["author"]
    url = COMMENTS_URL.format(cid=sample_content)
    mid = client.post(
        url,
        json={"body": "Original text"},
        headers=auth_header(author_token)
    ).get_json()["id"]
    edit_url = COMMENT_URL.format(cid=sample_content, mid=mid)
    with freeze_time(datetime.utcnow() + EDIT_WINDOW - timedelta(seconds=1)):
        fresh_token = login(client, author_data["email"], author_data["password"])\
                      .get_json()["access_token"]
        resp = client.put(edit_url, json={"body": "Edited text"}, headers=auth_header(fresh_token))
        assert resp.status_code == 200
        assert resp.get_json()["body"] == "Edited text"
    with freeze_time(datetime.utcnow() + EDIT_WINDOW + timedelta(seconds=1)):
        stale_token = login(client, author_data["email"], author_data["password"])\
                      .get_json()["access_token"]
        resp2 = client.put(edit_url, json={"body": "Too late"}, headers=auth_header(stale_token))
        assert resp2.status_code == 403
        assert resp2.get_json()["error"] == "You may not edit this comment"
def test_admin_cannot_edit(client, user_tokens, sample_content):
    author_token = user_tokens["author"][1]
    admin_token = user_tokens["admin"][1]
    url = COMMENTS_URL.format(cid=sample_content)
    mid = client.post(
        url,
        json={"body": "Author's comment"},
        headers=auth_header(author_token)
    ).get_json()["id"]
    edit_url = COMMENT_URL.format(cid=sample_content, mid=mid)
    resp = client.put(edit_url, json={"body": "Admin edit"}, headers=auth_header(admin_token))
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "You may not edit this comment"
def test_delete_by_author_and_admin_and_forbidden_for_others(client, user_tokens, sample_content):
    author_token = user_tokens["author"][1]
    commenter_token = user_tokens["commenter"][1]
    admin_token = user_tokens["admin"][1]
    url = COMMENTS_URL.format(cid=sample_content)
    mid1 = client.post(
        url,
        json={"body": "To be deleted"},
        headers=auth_header(author_token)
    ).get_json()["id"]
    del_url1 = COMMENT_URL.format(cid=sample_content, mid=mid1)
    resp0 = client.delete(del_url1, headers=auth_header(commenter_token))
    assert resp0.status_code == 403
    assert resp0.get_json()["error"] == "You may not delete this comment"
    resp1 = client.delete(del_url1, headers=auth_header(author_token))
    assert resp1.status_code == 200
    assert resp1.get_json()["message"] == "Comment deleted"
    mid2 = client.post(
        url,
        json={"body": "Admin delete"},
        headers=auth_header(author_token)
    ).get_json()["id"]
    del_url2 = COMMENT_URL.format(cid=sample_content, mid=mid2)
    resp2 = client.delete(del_url2, headers=auth_header(admin_token))
    assert resp2.status_code == 200
    assert resp2.get_json()["message"] == "Comment deleted"
def test_404_on_nonexistent_resources(client, user_tokens):
    author_token = user_tokens["author"][1]
    assert client.get(COMMENTS_URL.format(cid=9999)).status_code == 404
    assert client.post(
        COMMENTS_URL.format(cid=9999),
        json={"body": "X"},
        headers=auth_header(author_token)
    ).status_code == 404
    assert client.put(
        COMMENT_URL.format(cid=1, mid=9999),
        json={"body": "X"},
        headers=auth_header(author_token)
    ).status_code == 404
    assert client.delete(
        COMMENT_URL.format(cid=1, mid=9999),
        headers=auth_header(author_token)
    ).status_code == 404