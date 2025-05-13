from enum import Enum as PyEnum
from typing import Any, Dict, List
from flask import current_app
from sqlalchemy import Index, event, func
from sqlalchemy.orm import Query
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime
from . import db

def _query_get(self, ident):
    model = self._only_full_mapper_zero("get")
    return self.session.get(model, ident)
Query.get = _query_get

class UserRoleEnum(PyEnum):
    ADMIN = "Admin"
    TECHWRITER = "TechWriter"
    USER = "User"

class ContentTypeEnum(PyEnum):
    video = "video"
    audio = "audio"
    article = "article"  # Fixed inconsistency: "quote" was incorrectly used
    quote = "quote"
    Video = "video"  # These can be removed if not needed
    Audio = "audio"
    Article = "article"
    Quote = "quote"

class ContentStatusEnum(PyEnum):
    Draft = "Draft"
    Pending = "Pending"
    Published = "Published"
    Flagged = "Flagged"

class ReactionTypeEnum(PyEnum):
    like = "like"
    dislike = "dislike"

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action = db.Column(db.String(128), nullable=False)
    target_type = db.Column(db.String(64), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    def __repr__(self):
        return f"<AuditLog id={self.id} action={self.action} user_id={self.user_id}>"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    profile = db.relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    user_roles = db.relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    roles = association_proxy("user_roles", "role")
    refresh_tokens = db.relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    subscriptions = db.relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )
    wishlist_items = db.relationship(
        "Wishlist", back_populates="user", cascade="all, delete-orphan"
    )
    reactions = db.relationship(
        "Reaction", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )

    def get_primary_role(self):
        """Returns the first role as the primary role, defaulting to 'User' if none."""
        return self.roles[0].name if self.roles else 'User'

    def __repr__(self):
        return f"<User id={self.id} email={self.email} name={self.name}>"

class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(128))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(512))
    social_links = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    user = db.relationship("User", back_populates="profile")
    def __repr__(self):
        return f"<UserProfile id={self.id} user_id={self.user_id}>"

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))

    role_permissions = db.relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    user_roles = db.relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )
    users = association_proxy("user_roles", "user")
    def __repr__(self):
        return f"<Role id={self.id} name={self.name}>"

@event.listens_for(Role.__table__, "after_create")
def seed_roles(target, connection, **kw):
    if current_app and current_app.config.get("TESTING"):
        return
    count = connection.execute("SELECT COUNT(*) FROM roles").scalar()
    if count == 0:
        for role in UserRoleEnum:
            connection.execute(
                target.insert().values(name=role.value, description=role.value)
            )

class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    role_permissions = db.relationship(
        "RolePermission", backref="permission", cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Permission id={self.id} name={self.name}>"

class UserRole(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id = db.Column(
        db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    __table_args__ = (db.UniqueConstraint("user_id", "role_id", name="uq_user_role"),)
    user = db.relationship("User", back_populates="user_roles")
    role = db.relationship("Role", back_populates="user_roles")
    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"

class RolePermission(db.Model):
    __tablename__ = "role_permissions"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(
        db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    permission_id = db.Column(
        db.Integer, db.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    )
    __table_args__ = (db.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)
    role = db.relationship("Role", back_populates="role_permissions")
    def __repr__(self):
        return f"<RolePermission role_id={self.role_id} permission_id={self.permission_id}>"

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    created_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    contents = db.relationship(
        "Content", back_populates="category", cascade="all, delete-orphan"
    )
    subscribers = db.relationship(
        "Subscription", back_populates="category", cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Category id={self.id} name={self.name}>"

@event.listens_for(Category.__table__, "after_create")
def seed_categories(target, connection, **kw):
    if current_app and current_app.config.get("TESTING"):
        return
    count = connection.execute("SELECT COUNT(*) FROM categories").scalar()
    if count == 0:
        hardcoded_categories = [
            {"name": "Fullstack Development", "description": "Content related to fullstack development."},
            {"name": "Cyber Security", "description": "Content related to cybersecurity practices."},
            {"name": "Data Science", "description": "Content related to data science and analytics."},
            {"name": "Mobile Development", "description": "Content related to mobile app development."},
            {"name": "Artificial Intelligence", "description": "Content related to AI and machine learning."}
        ]
        for cat in hardcoded_categories:
            connection.execute(
                target.insert().values(name=cat["name"], description=cat["description"], created_by=1)
            )

class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    contents = db.relationship(
        "ContentTag", back_populates="tag", cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Tag id={self.id} name={self.name}>"

class Content(db.Model):
    __tablename__ = "contents"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text)
    media_url = db.Column(db.String(512))
    content_type = db.Column(db.Enum(ContentTypeEnum), nullable=False)
    status = db.Column(
        db.Enum(ContentStatusEnum),
        default=ContentStatusEnum.Draft,
        nullable=False,
    )
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL")
    )
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    author = db.relationship("User", backref="contents")
    category = db.relationship("Category", back_populates="contents")
    history = db.relationship(
        "ContentHistory", back_populates="content", cascade="all, delete-orphan"
    )
    tags = db.relationship(
        "ContentTag", back_populates="content", cascade="all, delete-orphan"
    )
    subscriptions = db.relationship(
        "Subscription", back_populates="content", cascade="all, delete-orphan"
    )
    wishlist_items = db.relationship(
        "Wishlist", back_populates="content", cascade="all, delete-orphan"
    )
    reactions = db.relationship(
        "Reaction", back_populates="content", cascade="all, delete-orphan"
    )
    flags = db.relationship(
        "Flag", back_populates="content", cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", back_populates="content", cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Content id={self.id} title={self.title}>"

class ContentTag(db.Model):
    __tablename__ = "content_tags"
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    tag_id = db.Column(
        db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
    )
    __table_args__ = (
        db.UniqueConstraint("content_id", "tag_id", name="uq_content_tag"),
    )
    content = db.relationship("Content", back_populates="tags")
    tag = db.relationship("Tag", back_populates="contents")
    def __repr__(self):
        return f"<ContentTag content_id={self.content_id} tag_id={self.tag_id}>"

class ContentHistory(db.Model):
    __tablename__ = "content_histories"
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(256))
    body = db.Column(db.Text)
    media_url = db.Column(db.String(512))
    edited_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    edited_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    content = db.relationship("Content", back_populates="history")
    def __repr__(self):
        return f"<ContentHistory id={self.id} content_id={self.content_id}>"

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE"))
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    post = db.relationship("Post", backref="post_comments_ref", overlaps="comment_post,post_comments")
    user = db.relationship("User", back_populates="comments")
    children = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
    )
    def __repr__(self):
        return f"<Comment id={self.id} post_id={self.post_id}>"

class Subscription(db.Model):
    __tablename__ = "subscriptions"
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=True
    )
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", back_populates="subscriptions")
    category = db.relationship("Category", back_populates="subscribers")
    content = db.relationship("Content", back_populates="subscriptions")
    __table_args__ = (
        Index("ix_subscriptions_user_id", "user_id"),
        Index("ix_subscriptions_category_id", "category_id"),
    )
    def __repr__(self):
        return f"<Subscription user_id={self.user_id} category_id={self.category_id}>"

class Wishlist(db.Model):
    __tablename__ = "wishlists"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", back_populates="wishlist_items")
    content = db.relationship("Content", back_populates="wishlist_items")
    def __repr__(self):
        return f"<Wishlist id={self.id} user_id={self.user_id}>"

class Reaction(db.Model):
    __tablename__ = "reactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    type = db.Column(db.Enum(ReactionTypeEnum), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", back_populates="reactions")
    content = db.relationship("Content", back_populates="reactions")

class Flag(db.Model):
    __tablename__ = "flags"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    reason = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", backref="flags")
    content = db.relationship("Content", back_populates="flags")
    def __repr__(self):
        return f"<Flag id={self.id} reason={self.reason}>"

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=True
    )
    message = db.Column(db.String(256), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", back_populates="notifications")
    content = db.relationship("Content", back_populates="notifications")
    def __repr__(self):
        return f"<Notification id={self.id} message={self.message}>"

class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = db.Column(db.String(36), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", back_populates="refresh_tokens")
    def __repr__(self):
        return f"<RefreshToken jti={self.token} revoked={self.revoked}>"

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(128), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    likes = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    post_comments = db.relationship("Comment", backref="comment_post", cascade="all, delete-orphan", overlaps="post,post_comments_ref")
    def __repr__(self):
        return f"<Post id={self.id} title={self.title}>"

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = db.Column(db.String(256), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", backref="password_reset_tokens")
    def __repr__(self):
        return f"<PasswordResetToken id={self.id} user_id={self.user_id}>"

class PhoneOTP(db.Model):
    __tablename__ = "phone_otps"
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    def __repr__(self):
        return f"<PhoneOTP id={self.id} phone={self.phone_number} code={self.otp_code}>"

class EmailVerificationToken(db.Model):
    __tablename__ = "email_verification_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = db.Column(db.String(256), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    user = db.relationship("User", backref="email_verification_tokens")
    def __repr__(self):
        return f"<EmailVerificationToken id={self.id} user_id={self.user_id}>"

Index("ix_refresh_token_token", RefreshToken.token)
Index("ix_password_reset_token_token", PasswordResetToken.token)
Index("ix_email_verification_token_token", EmailVerificationToken.token)