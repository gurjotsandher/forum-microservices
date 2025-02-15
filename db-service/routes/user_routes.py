from flask import Blueprint, request, jsonify
from models import User
from schemas import UserSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.db_utils import get_tenant_db_url
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from common.error_handlers import get_dynamic_logger

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
    logger = get_dynamic_logger()  # Initialize the logger here

    tenant_id = request.headers.get('X-Tenant-ID')  # Get tenant ID from request header
    try:
        data = user_schema.load(request.get_json())  # Automatically validates input
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")  # Log validation error
        return jsonify({"error": err.messages}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        logger.warning("Missing required fields: username, email, or password.")  # Log missing fields
        return jsonify({"error": "Missing required fields"}), 400

    # Get the tenant-specific database session
    db_session = get_db_session(tenant_id)

    try:
        # Check if the email is already registered in the tenant's database
        if db_session.query(User).filter_by(email=email).first():
            logger.warning(f"Email {email} already registered for tenant {tenant_id}.")  # Log duplicate email
            return jsonify({"error": "Email already registered"}), 409
        if db_session.query(User).filter_by(username=username).first():
            logger.warning(f"Username {username} already exists for tenant {tenant_id}.")  # Log duplicate username
            return jsonify({"error": "Username already exists"}), 409

        # Create the user and hash the password
        user = User(username=username, email=email, password=password, role='user')

        # Add the user to the tenant-specific database
        db_session.add(user)
        db_session.commit()

        logger.info(f"User {username} registered successfully for tenant {tenant_id}.")  # Log successful registration
        return jsonify({"message": f"User {username} registered successfully"}), 201

    except SQLAlchemyError as e:
        # Log database error
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login_user():
    """Authenticate a user with email and password."""
    logger = get_dynamic_logger()  # Initialize the logger here

    tenant_id = request.headers.get('X-Tenant-ID')
    data = request.get_json()
    db_session = get_db_session(tenant_id)

    try:
        user = db_session.query(User).filter_by(email=data['email']).first()
        if user is None or not user.check_password(data['password']):
            logger.warning(f"Login failed for user {data['email']} in tenant {tenant_id}.")  # Log failed login
            return jsonify({"error": "Invalid email or password"}), 401

        logger.info(f"User {user.username} logged in successfully for tenant {tenant_id}.")  # Log successful login
        return jsonify({"id": user.id, "username": user.username}), 200

    except SQLAlchemyError as e:
        # Log database error
        logger.error(f"Database error occurred during login: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

    except Exception as e:
        # Log unexpected error
        logger.error(f"Unexpected error occurred during login: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
