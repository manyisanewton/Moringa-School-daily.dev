from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from . import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    google_id = db.Column(db.String(256), nullable=True) # auth login
    github_id = db.Column(db.String(256), nullable=True) # auth login
    role = db.Column(db.String(50), nullable=False, default="user")

    # time stamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'
