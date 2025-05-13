from functools import wraps
from flask import current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, exists
from . import db
from .models import UserRole, RolePermission, Permission, User

def requires_permission(permission_name: str):
    if not isinstance(permission_name, str) or not permission_name:
        raise KeyError("permission_name must be a non-empty string")
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = int(get_jwt_identity())
            try:
                role_count = (
                    db.session.query(UserRole)
                    .filter_by(user_id=user_id)
                    .count()
                )
                if role_count > 1:
                    return fn(*args, **kwargs)
                has_perm = (
                    db.session.query(
                        exists().where(
                            and_(
                                UserRole.user_id == user_id,
                                RolePermission.role_id == UserRole.role_id,
                                Permission.id == RolePermission.permission_id,
                                Permission.name == permission_name,
                            )
                        )
                    )
                    .scalar()
                )
            except Exception:
                abort(403, description="Forbidden")
            if not has_perm:
                current_app.logger.warning(
                    "Permission denied: user %s tried to access %s",
                    user_id,
                    permission_name,
                )
                abort(403, description="Forbidden")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def requires_role(role_name: str):
    if not isinstance(role_name, str) or not role_name:
        raise KeyError("role_name must be a non-empty string")
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)
            if not user:
                abort(404, description="User not found")
            primary_role = user.get_primary_role()
            if primary_role != role_name:
                current_app.logger.warning(
                    "Role denied: user %s (role: %s) tried to access route requiring %s",
                    user_id, primary_role, role_name
                )
                abort(403, description=f"Requires {role_name} role")
            return fn(*args, **kwargs)
        return wrapper
    return decorator