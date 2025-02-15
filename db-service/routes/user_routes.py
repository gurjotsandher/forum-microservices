from flask import Blueprint, request, jsonify
from models import User
from schemas import UserSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.db_utils import get_tenant_db_url
from marshmallow import ValidationError

user_bp = Blueprint('user', __name__)
user_schema = UserSchema()

def get_db_session(tenant_id):
    """Get a session for the tenant's specific database."""
    db_url = get_tenant_db_url(tenant_id)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()

@user_bp.route('/register', methods=['POST'])
def register_user():
    """Register a new user with Marshmallow validation."""
    tenant_id = request.headers.get('X-Tenant-ID')  # Get tenant ID from request header
    try:
        data = user_schema.load(request.get_json())  # Automatically validates input
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    # Get the tenant-specific database session
    db_session = get_db_session(tenant_id)

    # Check if the email is already registered in the tenant's database
    if db_session.query(User).filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    if db_session.query(User).filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    # Create the user and hash the password
    user = User(username=username, email=email, password=password, role='user')

    # Add the user to the tenant-specific database
    db_session.add(user)
    db_session.commit()

    return jsonify({"message": f"User {username} registered successfully"}), 201

@user_bp.route('/login', methods=['POST'])
def login_user():
    """Authenticate a user with email and password."""
    tenant_id = request.headers.get('X-Tenant-ID')
    data = request.get_json()
    db_session = get_db_session(tenant_id)

    user = db_session.query(User).filter_by(email=data['email']).first()
    print(f"User found => {user}")
    if user is None or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"id": user.id, "username": user.username}), 200
