from flask import Blueprint, request, jsonify
from common.auth_utils import generate_token
import requests

auth_bp = Blueprint('auth', __name__)

# Hardcoded URL for db-service (running on port 5003)
DB_SERVICE_URL = "http://db-service:5003"

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    data = request.get_json()
    tenant_id = request.headers.get('X-Tenant-ID')  # Get tenant ID from request header
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    # Make a request to the db-service to save the new user
    create_user_url = f"{DB_SERVICE_URL}/db/user/register"  # Hardcoded create user URL
    user_data = {"username": username, "email": email, "password": password}

    headers = {"X-Tenant-ID": tenant_id}

    db_response = requests.post(create_user_url, json=user_data, headers=headers)

    if db_response.status_code == 201:
        return jsonify({"message": f"User {username} registered successfully"}), 201
    else:
        return jsonify({"error": "Failed to register user"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    tenant_id = request.headers.get('X-Tenant-ID')  # Get tenant ID from request header
    email = data.get('email')
    password = data.get('password')

    # Find the user by email in the tenant's database
    user = db_session.query(User).filter_by(email=email).first()

    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT token for the user
    token = generate_token(user.id, current_app.config['JWT_SECRET_KEY'])
    print(f"Token => {token}")

    return jsonify({"token": token}), 200

# Health check endpoint
@auth_bp.route('/health', methods=['GET'])
def health():
    """Basic health check for the service."""
    return "OK", 200