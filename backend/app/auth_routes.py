from flask import Blueprint, request, jsonify, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from .models import db, User
from .utils import hash_password, create_token, password_check

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

def init_oauth(app):
    google_bp = make_google_blueprint(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=["profile", "email"],
        redirect_url='http://localhost:5000/auth/google/authorized',
        redirect_to='auth_bp.google_login'
    )
    # OAuth blueprints
    app.register_blueprint(google_bp, url_prefix='/auth/google')

# Google login
@auth_bp.route('/google-login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    # acquire user information
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return jsonify({'error': 'Failed to fetch user info'}), 400
    
    user_info = resp.json()

    # get the email and name 
    email = user_info.get('email')
    name = user_info.get('name')

    if not email:
        return jsonify({'error': 'Email not available from Google.'}), 400

    # if no user create new user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, phone=None, password_hash=None, role='user')
        db.session.add(user)
        db.session.commit()

    # token
    token = create_token(user.id, user.role)

    return jsonify({
        'message': 'Google login successful!',
        'token': token,
        'email': user.email,
        'name': user.name
    }), 200


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




 


        
