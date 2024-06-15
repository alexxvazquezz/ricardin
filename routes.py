from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from itsdangerous import URLSafeSerializer as Serializer
from config import Config
import time

bp = Blueprint('api', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required.'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 400

    new_user = User(email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully.', 'user': new_user.to_dict()}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required.'}), 400
    
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    
    login_user(user)

    # Generate access token
    s = Serializer(Config.SECRET_KEY)
    expiration_time = int(time.time()) + 3600
    token = s.dumps({'user_id': user.id, 'expires': expiration_time})

    return jsonify({'message': 'Login successful.', 'access_token': token}), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'messsage': 'Logout successful.'}), 200

@bp.route('/users', methods=['GET'])
@login_required
def get_all_users():
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200

