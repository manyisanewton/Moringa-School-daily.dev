import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os


# hash the users password for security purposes during registration
def hash_password(password):
    return generate_password_hash(password)

# check the password for a match during login
def password_check(password, password_hash):
    return check_password_hash(password_hash, password)

# a jwt token
def create_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        # expiration time of a token
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    secret_key = os.getenv('SECRET_KEY', 'secretkey')
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

# ensure that a user is logged in
def decode_access_token(token):
    secret_key = os.getenv('SECRET_KEY', 'secretkey')
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # for expired tokens
    except jwt.InvalidTokenError:
        return None
    