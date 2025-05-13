import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from backend.app.models import User, PasswordResetToken, PhoneOTP
from backend.app import db, bcrypt
from backend.config import TestConfig
new_pw = "Ht7!dV9#kP2$mX6b"
@pytest.fixture(autouse=True)
def seed_user(app):
    with app.app_context():
        db.session.query(PasswordResetToken).delete()
        db.session.query(PhoneOTP).delete()
        db.session.query(User).delete()
        pw_hash = bcrypt.generate_password_hash("Gk8^Hn3&Tz5*Px7R").decode()
        user = User(
            email="ursula.parker@example.com",
            name="Ursula Parker",
            password_hash=pw_hash,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        yield
        db.session.rollback()
def test_request_missing_payload(client):
    r = client.post("/auth/request-password-reset", json={})
    assert r.status_code == 400
def test_request_password_reset_sms_flow(client, monkeypatch, app):
    with app.app_context():
        user = User.query.filter_by(email="ursula.parker@example.com").one()
        user.phone_number = "+25488998899"
        user.is_active = True
        db.session.commit()
    sent = {}
    class DummyVerifications:
        def create(self, **kwargs):
            sent.update(kwargs)
    class DummyVerifyService:
        @property
        def verifications(self):
            return DummyVerifications()
    class DummyClient:
        def __init__(self, sid, token):
            pass
        @property
        def verify(self):
            return self
        def services(self, sid):
            return DummyVerifyService()
    monkeypatch.setattr("backend.app.password_reset.TwilioClient", DummyClient)
    r = client.post("/auth/request-password-reset-sms", json={"identifier": "+25488998899"})
    assert r.status_code == 200
    assert sent["to"] == "+25488998899"
    assert sent["channel"] == "sms"
def test_request_password_reset_sms_with_bad_number(client):
    r = client.post("/auth/request-password-reset-sms", json={"identifier": "088998899"})
    assert r.status_code == 400
    err = r.get_json()["error"]
    assert "identifier" in err
    assert "E.164" in err["identifier"][0]
def test_reset_password_sms_flow(client, monkeypatch, app):
    with app.app_context():
        user = User.query.filter_by(email="ursula.parker@example.com").one()
        user.phone_number = "+25488998899"
        user.is_active = True
        db.session.commit()
    class DummyCheck:
        status = "approved"
    class DummyVerifyService:
        @property
        def verification_checks(self):
            return self
        def create(self, **kwargs):
            return DummyCheck()
    class DummyClient:
        def __init__(self, sid, token):
            pass
        @property
        def verify(self):
            return self
        def services(self, sid):
            return DummyVerifyService()
    monkeypatch.setattr("backend.app.password_reset.TwilioClient", DummyClient)
    r = client.post("/auth/reset-password-sms", json={
        "phone_number": "+25488998899",
        "otp_code": "888444",
        "new_password": new_pw,
        "confirm_password": new_pw
    })
    assert r.status_code == 200
    assert r.get_json()["message"] == "Password has been reset."
    with app.app_context():
        user = User.query.filter_by(phone_number="+25488998899").one()
        assert bcrypt.check_password_hash(user.password_hash, new_pw)
def test_reset_password_sms_with_bad_number(client):
    payload = {
        "phone_number": "088998899",
        "otp_code": "888444",
        "new_password": new_pw,
        "confirm_password": new_pw
    }
    r = client.post("/auth/reset-password-sms", json=payload)
    assert r.status_code == 400
    err = r.get_json()["error"]
    assert "Invalid phone number" in err
def test_reset_password_sms_with_incorrect_code(client, monkeypatch, app):
    with app.app_context():
        user = User.query.filter_by(email="ursula.parker@example.com").one()
        user.phone_number = "+25488998899"
        db.session.commit()
    class DummyCheck:
        status = "pending"
    class DummyVerifyService:
        @property
        def verification_checks(self):
            return self
        def create(self, **kwargs):
            return DummyCheck()
    class DummyClient:
        def __init__(self, sid, token):
            pass
        @property
        def verify(self):
            return self
        def services(self, sid):
            return DummyVerifyService()
        @property
        def messages(self):
            class Msg:
                def create(self, **kwargs):
                    return None
            return Msg()
    monkeypatch.setattr("backend.app.password_reset.TwilioClient", DummyClient)
    r = client.post("/auth/reset-password-sms", json={
        "phone_number": "+25488998899",
        "otp_code": "000000",
        "new_password": "M3x!c0$p!55@",
        "confirm_password": "M3x!c0$p!55@"
    })
    assert r.status_code == 400
    assert "Invalid or expired code." in r.get_json()["error"]