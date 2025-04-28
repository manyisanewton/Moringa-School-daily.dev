from flask import Blueprint, request, jsonify
from .models import db, User
from .utils import hash_password, create_token, password_check

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# Register
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    role = data.get('role', 'user')

    # confirm that all validations are provided
    if not all([name, email, phone, password, confirm_password]):
        return jsonify({'error': 'Missing required fields.'}), 400
    
    # confirm if the passwords match
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match!'}), 400
    
    # confirm if the user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists.'}), 409
    
    # create user: hash the password and store it
    new_user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        role=role
    )
    db.session.add(new_user)
    db.session.commit()

    # come up with a token
    token = create_token(new_user.id, new_user.role)

    return jsonify({
        'message': 'User registered successfully.',
        'token': token
    }), 201

# Login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # confirm all fields are filled
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    
    # confirm that user exists
    existing_user = User.query.filter_by(email=email).first()
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    # confirm that the password is correct
    if not password_check(password, existing_user.password_hash):
        return jsonify({'error': 'Invalid password'}), 401
    
    # come up with a token
    token = create_token(existing_user.id, existing_user.role)

    return jsonify({
        'message': 'Login successful',
        'token': token
    }), 200
