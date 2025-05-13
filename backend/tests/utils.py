import pytest
from flask_jwt_extended.utils import decode_token
from backend.app.models import Role, UserRole
from backend.app import db
def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
def register(client, creds):
    if "password" in creds and "confirm_password" not in creds:
        creds["confirm_password"] = creds["password"]
    return client.post("/auth/register", json=creds)
def login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password})
def get_tokens(client, email="emma.watson@example.com", password="Gt9@Xy2!QpL8#ZmR"):
    creds = {
        "name": "Emma Watson",
        "email": email,
        "password": password,
        "confirm_password": password,
    }
    r = register(client, creds)
    assert r.status_code in (201, 409)
    resp = login(client, email, password)
    data = resp.get_json() or {}
    return data["access_token"], data["refresh_token"]
def user_id_from_token(token):
    return int(decode_token(token)["sub"])
@pytest.fixture
def user_token(client):
    token, _ = get_tokens(client)
    return token
@pytest.fixture
def admin_token(client):
    with client.application.app_context():
        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        db.session.refresh(admin_role)
    creds = {
        "name": "Alice White",
        "email": "alice.white@example.com",
        "password": "Hp8&Lk2*Tx9!PnQ0",
        "role": "Admin",
    }
    r = register(client, creds)
    assert r.status_code in (201, 409)
    access, _ = get_tokens(client, email=creds["email"], password=creds["password"])
    uid = user_id_from_token(access)
    with client.application.app_context():
        if not UserRole.query.filter_by(user_id=uid, role_id=admin_role.id).first():
            db.session.add(UserRole(user_id=uid, role_id=admin_role.id))
            db.session.commit()
    return access