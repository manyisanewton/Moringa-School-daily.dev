import pytest

#  necessities from utils
from .utils import hash_password, password_check, create_token, decode_access_token

# password hashing and verification
def test_password_hashing_and_verification():
    
    password = 'randompassword123_'
    hashed = hash_password(password)

    assert password_check(password, hashed) == True
    assert password_check("wrongpassword", hashed) == False

# token creation and decoding
def test_token_creation_and_decoding():
    user_id = 1
    role = "user"
    token = create_token(user_id, role)
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded['user_id'] == user_id
    assert decoded['role'] == role
    