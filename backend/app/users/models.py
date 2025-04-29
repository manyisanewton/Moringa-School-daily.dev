from .. import db
import uuid

# Relationship table for followers
followers = db.Table('followers',
    db.Column('follower_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.String(36), db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, tech_writer, user
    is_active = db.Column(db.Boolean, default=True)
    profile = db.Column(db.JSON, default={})  # For storing user profile data
    subscriptions = db.Column(db.JSON, default=[])  # List of category IDs
    wishlist = db.Column(db.JSON, default=[])  # List of content IDs
    notification_preferences = db.Column(db.JSON, default=lambda: {
        'new_content': True,
        'like': True,
        'comment': True
    })  # Default: receive all notifications

    # Relationships for followers and following
    following = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    
from app.routes.notification_routes import notification_bp