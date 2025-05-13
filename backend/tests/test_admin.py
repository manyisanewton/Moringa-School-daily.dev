import pytest
from flask import Flask
from backend.app import db
from backend.app.models import User, Role, UserRole, Category, Content, ContentStatusEnum
from backend.tests.utils import register, login, auth_header
ADMIN_USERS_URL = "/admin/users"
ADMIN_DEACTIVATE_URL = "/admin/users/{uid}/deactivate"
ADMIN_PROMOTE_URL = "/admin/users/{uid}/promote/{role}"
ADMIN_CATEGORIES_URL = "/admin/categories"
ADMIN_APPROVE_URL = "/admin/contents/{cid}/approve"
ADMIN_FLAG_URL = "/admin/contents/{cid}/flag"
ADMIN_DELETE_URL = "/admin/contents/{cid}"
@pytest.fixture(autouse=True)
def seed_roles(app: Flask):
    with app.app_context():
        for name in ("Admin", "User", "TechWriter"):
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=name))
        db.session.commit()
@pytest.fixture
def admin_token(client):
    creds = {
        "name": "Olivia Jackson",
        "email": "olivia.jackson.admin@example.com",
        "password": "Xk9#Fp8&Jh2@QrT",
        "role": "Admin",
    }
    register(client, creds)
    with client.application.app_context():
        u = User.query.filter_by(email=creds["email"]).one()
        r = Role.query.filter_by(name="Admin").one()
        db.session.add(UserRole(user_id=u.id, role_id=r.id))
        db.session.commit()
    resp = login(client, creds["email"], creds["password"])
    return resp.get_json()["access_token"]
@pytest.fixture
def sample_content(client, admin_token, app):
    writer = {
        "name": "Liam Anderson",
        "email": "liam.anderson@example.com",
        "password": "Tb5@Qn7$WkX1!ZcV",
        "role": "TechWriter",
    }
    register(client, writer)
    with app.app_context():
        u  = User.query.filter_by(email=writer["email"]).one()
        tw = Role.query.filter_by(name="TechWriter").one()
        db.session.add(UserRole(user_id=u.id, role_id=tw.id))
        db.session.commit()
    token = login(client, writer["email"], writer["password"]).get_json()["access_token"]
    r = client.post(
        "/content",
        json={"title": "Test", "body": "x", "content_type": "article"},
        headers=auth_header(token)
    )
    cid = r.get_json().get("id")
    if cid is None:
        with app.app_context():
            cid = Content.query.order_by(Content.id.desc()).first().id
    return cid
class TestCreateUser:
    def test_happy_path(self, client, admin_token):
        payload = {
            "email": "jackie.brown.user@example.com",
            "password": "Yt4@Mk8&Nw3#LpQ",
            "roles": ["User"],
            "name": "Jackie Brown"
        }
        r = client.post(ADMIN_USERS_URL, json=payload, headers=auth_header(admin_token))
        assert r.status_code == 201
        data = r.get_json()
        assert data["message"] == "User created."
        new_id = data["id"]
        with client.application.app_context():
            u = db.session.get(User, new_id)
            assert u.email == payload["email"]
            assert u.name  == payload["name"]
            assert any(ur.role.name == "User" for ur in u.user_roles)
    def test_name_defaults_to_email(self, client, admin_token):
        payload = {
            "email": "jane.cornell.user@example.com",
            "password": "Gh7%Rt4!Ux9$VzW",
            "roles": ["User"]
        }
        r = client.post(ADMIN_USERS_URL, json=payload, headers=auth_header(admin_token))
        assert r.status_code == 201
        new_id = r.get_json()["id"]
        with client.application.app_context():
            u = db.session.get(User, new_id)
            assert u.name == u.email
    @pytest.mark.parametrize("bad_payload", [
        {},
        {"email": "bad", "password": "short", "roles": []},
        {"email": "x@x.com", "password": "NoDigitsHere", "roles": ["User"]},
    ])
    def test_invalid_payload(self, client, admin_token, bad_payload):
        r = client.post(ADMIN_USERS_URL, json=bad_payload, headers=auth_header(admin_token))
        assert r.status_code == 400
    def test_duplicate_email(self, client, admin_token):
        payload = {
            "email": "emma.williams@example.com",
            "password": "Lp3#Df9!Qw7$RtY",
            "roles": ["User"]
        }
        r1 = client.post(ADMIN_USERS_URL, json=payload, headers=auth_header(admin_token))
        assert r1.status_code == 201
        r2 = client.post(ADMIN_USERS_URL, json=payload, headers=auth_header(admin_token))
        assert r2.status_code == 409
        assert "already exists" in r2.get_json()["error"]
    def test_role_not_found(self, client, admin_token):
        payload = {
            "email": "kate.mitchell@example.com",
            "password": "Zm5@Rt2#Yh8!QwP",
            "roles": ["NoRole"]
        }
        r = client.post(ADMIN_USERS_URL, json=payload, headers=auth_header(admin_token))
        assert r.status_code == 400
        assert "not found" in r.get_json()["errors"]["roles"][0]
    def test_already_has_role(self, client, admin_token):
        creds = {
            "name": "Sam Brown",
            "email": "samantha.brown@example.com",
            "password": "Ui8#Er3!Yt5$WqZ",
            "role": "User",
        }
        register(client, creds)
        with client.application.app_context():
            u  = User.query.filter_by(email=creds["email"]).one()
            ur = Role.query.filter_by(name="User").one()
            db.session.add(UserRole(user_id=u.id, role_id=ur.id))
            db.session.commit()
            uid = u.id
        r = client.post(
            ADMIN_PROMOTE_URL.format(uid=uid, role="User"),
            headers=auth_header(admin_token)
        )
        assert r.status_code == 400
        assert "already has that role" in r.get_json()["error"]
class TestCreateCategory:
    def test_happy_path(self, client, admin_token):
        payload = {"name": "DevOps", "description": "Ops stuff"}
        r = client.post(ADMIN_CATEGORIES_URL, json=payload, headers=auth_header(admin_token))
        assert r.status_code == 201
        data = r.get_json()
        assert data["message"] == "Category created."
        with client.application.app_context():
            cat = db.session.get(Category, data["id"])
            assert cat.name == payload["name"]
    @pytest.mark.parametrize("bad_payload", [
        {},
        {"name": ""},
        {"name": "x"*65},
        {"name": "Cat", "description": "x"*300},
    ])
    def test_invalid_payload(self, client, admin_token, bad_payload):
        r = client.post(ADMIN_CATEGORIES_URL, json=bad_payload, headers=auth_header(admin_token))
        assert r.status_code == 400
    def test_duplicate_category(self, client, admin_token):
        payload = {"name": "Ops", "description": "d"}
        client.post(ADMIN_CATEGORIES_URL, json=payload, headers=auth_header(admin_token))
        r2 = client.post(ADMIN_CATEGORIES_URL, json=payload, headers=auth_header(admin_token))
        assert r2.status_code == 409
class TestContentModeration:
    def test_approve(self, client, admin_token, sample_content):
        r = client.post(
            ADMIN_APPROVE_URL.format(cid=sample_content),
            headers=auth_header(admin_token)
        )
        assert r.status_code == 200
        with client.application.app_context():
            c = db.session.get(Content, sample_content)
            assert c.status == ContentStatusEnum.Published
    def test_flag(self, client, admin_token, sample_content):
        payload = {"reason": "Inappropriate"}
        r = client.post(
            ADMIN_FLAG_URL.format(cid=sample_content),
            json=payload,
            headers=auth_header(admin_token)
        )
        assert r.status_code == 200
        assert r.get_json()["reason"] == payload["reason"]
        with client.application.app_context():
            c = db.session.get(Content, sample_content)
            assert c.status == ContentStatusEnum.Flagged
    def test_flag_missing_reason(self, client, admin_token, sample_content):
        r = client.post(
            ADMIN_FLAG_URL.format(cid=sample_content),
            json={}, headers=auth_header(admin_token)
        )
        assert r.status_code == 400
    def test_delete(self, client, admin_token, sample_content):
        r = client.delete(
            ADMIN_DELETE_URL.format(cid=sample_content),
            headers=auth_header(admin_token)
        )
        assert r.status_code == 200
        with client.application.app_context():
            assert db.session.get(Content, sample_content) is None
    @pytest.mark.parametrize("method,url,payload", [
        ("post", ADMIN_APPROVE_URL.format(cid=12345), {}),
        ("post", ADMIN_FLAG_URL.format(cid=12345), {}),
        ("delete", ADMIN_DELETE_URL.format(cid=12345), None),
    ])
    def test_not_found(self, client, admin_token, method, url, payload):
        call = getattr(client, method)
        kwargs = {} if payload is None else {"json": payload}
        r = call(url, headers=auth_header(admin_token), **kwargs)
        assert r.status_code == 404
    def test_non_admin_forbidden(self, client, sample_content):
        creds = {
            "name": "Carl Hughes",
            "email": "carl.hughes@example.com",
            "password": "Bd5@Kj2#Nh9$ZxW",
            "role": "User",
        }
        register(client, creds)
        tok = login(client, creds["email"], creds["password"]).get_json()["access_token"]
        r1 = client.post(ADMIN_USERS_URL, json={}, headers=auth_header(tok))
        assert r1.status_code == 403
        r2 = client.post(
            ADMIN_APPROVE_URL.format(cid=sample_content),
            headers=auth_header(tok)
        )
        assert r2.status_code == 403