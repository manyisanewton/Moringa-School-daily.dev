import os
import sys
import pytest
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from backend.run import create_app
from backend.app import db as _db
from flask_jwt_extended import create_access_token
@pytest.fixture(scope="session")
def app():
    return create_app("testing")
@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()
@pytest.fixture(autouse=True)
def _db_setup(app):
    with app.app_context():
        _db.create_all()
    yield
    with app.app_context():
        _db.drop_all()
def get_tokens(client, email="emma.watson@example.com", password="Gt9@Xy2!QpL8#ZmR"):
    r = client.post("/auth/register", json={
        "name": "Emma Watson",
        "email": email,
        "password": password,
        "confirm_password": password,
        "role": "User",
    })
    assert r.status_code in (201, 409)
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    data = r.get_json()
    return data["access_token"], data["refresh_token"]
@pytest.fixture
def user_token(client):
    token, _ = get_tokens(client)
    return token
@pytest.fixture
def admin_token(client, app):
    from backend.app.models import Role
    with app.app_context():
        if not Role.query.filter_by(name="Admin").first():
            admin_role = Role(name="Admin", description="Administrator")
            _db.session.add(admin_role)
            _db.session.commit()
    email = "alice.white@example.com"
    password = "Hp8&Lk2*Tx9!PnQ0"
    client.post("/auth/register", json={
        "name": "Alice White",
        "email": email,
        "password": password,
        "confirm_password": password,
        "role": "Admin",
    })
    at, _ = get_tokens(client, email=email, password=password)
    return at