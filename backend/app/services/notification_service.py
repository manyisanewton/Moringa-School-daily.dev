from app.models.notification import Notification
from app.extensions import db

class NotificationService:

    @staticmethod
    def create_notification(user_id, message):
        notification = Notification(user_id=user_id, message=message)
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_user_notifications(user_id):
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(notification_id):
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification
