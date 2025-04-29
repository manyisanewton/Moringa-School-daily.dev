from flask import Blueprint, request, jsonify
from app.services.notification_service import NotificationService

notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('/create', methods=['POST'])
def create_notification():
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({'error': 'user_id and message are required'}), 400

    notification = NotificationService.create_notification(user_id, message)
    return jsonify(notification.to_dict()), 201

@notification_bp.route('/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    notifications = NotificationService.get_user_notifications(user_id)
    return jsonify([n.to_dict() for n in notifications]), 200

@notification_bp.route('/mark-read/<int:notification_id>', methods=['PUT'])
def mark_notification_as_read(notification_id):
    notification = NotificationService.mark_as_read(notification_id)
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    return jsonify(notification.to_dict()), 200
