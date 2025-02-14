from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import User
from common.auth_utils import generate_token
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

auth_bp = Blueprint('auth', __name__)

def get_tenant_db_url(tenant_id):
    """Fetch the database URL for a tenant from config-service."""
    config_service_url = f"http://config-service:5002/config/get-config/{tenant_id}"

    # Send GET request to fetch config from config-service
    response = requests.get(config_service_url, headers={"Authorization": f"Bearer {current_app.config['JWT_SECRET_KEY']}"})
    if response.status_code == 200:
        print("Response successful")
        config_data = response.json()
        return config_data.get("database_url")
    else:
        raise Exception(f"Failed to fetch config for tenant {tenant_id}. Status Code: {response.status_code}")

def get_db_session(tenant_id):
    """Get a session for the tenant's specific database."""
    db_url = get_tenant_db_url(tenant_id)
    print('db_url =>' + str(db_url))
    engine = create_engine(db_url)
    print('Engine created')
    Session = sessionmaker(bind=engine)
    print("Session established")
    return Session()

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

    # Get the tenant-specific database session
    db_session = get_db_session(tenant_id)

    # Check if the email is already registered in the tenant's database
    if db_session.query(User).filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # Create the user and hash the password
    user = User(username=username, email=email, password=password, role='user')
    print(f"User created: {user}")
    # Add the user to the tenant-specific database
    db_session.add(user)
    db_session.commit()

    return jsonify({"message": f"User {username} registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    tenant_id = request.headers.get('X-Tenant-ID')  # Get tenant ID from request header
    email = data.get('email')
    password = data.get('password')

    # Get the tenant-specific database session
    db_session = get_db_session(tenant_id)
    print(f"db session =>  {db_session}")

    # Find the user by email in the tenant's database
    user = db_session.query(User).filter_by(email=email).first()
    print(f"User => {user}")

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