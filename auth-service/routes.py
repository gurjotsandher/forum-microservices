from flask import Blueprint, request, jsonify, current_app
import requests
from werkzeug.security import generate_password_hash
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    data = request.get_json()

    # Retrieve the tenant ID from the header
    tenant_id = request.headers.get('X-Tenant-ID')
    if not tenant_id:
        return jsonify({"error": "Tenant ID missing in header"}), 400

    # Retrieve user information from the request body
    username = data.get('username')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    # Validate the input
    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate email format (simplified check)
    if '@' not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # Prepare the user data for the db-service
    # IMPORTANT: The password is being double hashed we need to remove that in db-service
    user_data = {"username": username, "email": email, "password": password}

    # Set up the request headers with the tenant ID
    headers = {"X-Tenant-ID": tenant_id}

    try:
        # Make a request to the db-service to save the new user
        create_user_url = f"{Config.DB_SERVICE_URL}/db/user/register"
        db_response = requests.post(create_user_url, json=user_data, headers=headers)

        # Check the db-service response
        if db_response.status_code == 201:
            return jsonify({"message": f"User {username} registered successfully"}), 201
        else:
            # Log the error from db-service and return a 500 error
            current_app.logger.error(f"Failed to register user: {db_response.json()}")
            return jsonify({"error": "Failed to register user", "details": db_response.json()}), 500
    except requests.exceptions.RequestException as e:
        # Log request exception errors
        current_app.logger.error(f"Error while making request to db-service: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    tenant_id = request.headers.get('X-Tenant-ID')  # Get tenant ID from request header
    email = data.get('email')
    password = data.get('password')

    user_data = {"email": email, "password": password}
    headers = {"X-Tenant-ID": tenant_id}

    try:
        get_login_url = f"{Config.DB_SERVICE_URL}/db/user/login"
        db_response = requests.post(get_login_url, json=user_data, headers=headers)
        if db_response.status_code == 200:
            return jsonify({"message": f"Successfully logged in user {db_response.json()['username']}"}), 200
        else:
            # Log the error from db-service and return a 500 error
            current_app.logger.error(f"Failed to login user: {db_response.json()}")
            return jsonify({"error": "Failed to login user", "details": db_response.json()}), 500

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error while making request to db-service: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Health check endpoint
@auth_bp.route('/health', methods=['GET'])
def health():
    """Basic health check for the service."""
    return "OK", 200