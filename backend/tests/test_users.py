import pytest
from flask_jwt_extended.utils import decode_token
from backend.app.models import UserProfile, AuditLog
from backend.tests.utils import auth_header, get_tokens, user_id_from_token
from sqlalchemy.exc import SQLAlchemyError
from backend.app import db
def test_get_profile_requires_auth(client):
    r = client.get("/users/me/profile")
    assert r.status_code == 401
def test_update_profile_requires_auth(client):
    r = client.put("/users/me/profile", json={})
    assert r.status_code == 401
def test_get_my_profile_creates_once(client, user_token, app):
    uid = user_id_from_token(user_token)
    with app.app_context():
        db.session.query(UserProfile).delete()
        db.session.commit()
    r1 = client.get("/users/me/profile", headers=auth_header(user_token))
    assert r1.status_code == 200
    r2 = client.get("/users/me/profile", headers=auth_header(user_token))
    assert r2.status_code == 200
    with app.app_context():
        count = db.session.query(UserProfile).filter_by(user_id=uid).count()
        assert count == 1
def test_update_my_profile_persists(client, user_token, app):
    p = {
        "name": "Alice McLaren",
        "bio": "Dev",
        "avatar_url": "http://ex.com/a.png",
        "social_links": "http://t.co"
    }
    r = client.put("/users/me/profile", json=p, headers=auth_header(user_token))
    assert r.status_code == 200
    with app.app_context():
        up = db.session.query(UserProfile).filter_by(
            user_id=user_id_from_token(user_token)
        ).one()
        assert (
            up.name == "Alice"
            and up.bio == "Dev"
            and up.avatar_url == "http://ex.com/a.png"
            and up.social_links == "http://t.co"
        )
def test_invalid_name_and_social_links_length(client, user_token):
    long_name = "a" * 129
    long_links = "l" * 513
    r1 = client.put("/users/me/profile", json={"name": long_name}, headers=auth_header(user_token))
    assert r1.status_code == 400 and "name" in r1.get_json()["errors"]
    r2 = client.put("/users/me/profile", json={"social_links": long_links}, headers=auth_header(user_token))
    assert r2.status_code == 400 and "social_links" in r2.get_json()["errors"]
def test_promote_user_nonexistent_role(client, admin_token):
    tok, _ = get_tokens(
        client,
        email="christiano.ronaldo@example.com",
        password="qM#82Tf@Ln4x"
    )
    uid = user_id_from_token(tok)
    r = client.post(f"/users/{uid}/promote/NoRole", headers=auth_header(admin_token))
    assert r.status_code == 404
def test_promote_user_db_error(monkeypatch, client, admin_token):
    tok, _ = get_tokens(
        client,
        email="shawn.paul@example.com",
        password="V7g!rPz9^kL3"
    )
    uid = user_id_from_token(tok)
    def bad_commit():
        raise SQLAlchemyError()
    monkeypatch.setattr(db.session, "commit", bad_commit)
    r = client.post(f"/users/{uid}/promote/Admin", headers=auth_header(admin_token))
    assert r.status_code == 500
def test_audit_logs_for_actions(client, user_token, admin_token, app):
    with app.app_context():
        db.session.query(AuditLog).delete()
        db.session.commit()
    client.get("/users/me/profile", headers=auth_header(user_token))
    client.put("/users/me/profile", json={"bio": "X"}, headers=auth_header(user_token))
    tok, _ = get_tokens(
        client,
        email="halland.grey@example.com",
        password="Zl!84Dp^Rm2w"
    )
    pu_id = user_id_from_token(tok)
    client.post(f"/users/{pu_id}/promote/TechWriter", headers=auth_header(admin_token))
    with app.app_context():
        acts = [alog.action for alog in db.session.query(AuditLog).all()]
        assert "get_profile" in acts
        assert "update_profile" in acts
        assert "promote_user" in acts