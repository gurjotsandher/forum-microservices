from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    tenant_id = request.headers.get('X-Tenant-ID')
    return jsonify({"message": f"Mock login success for tenant: {tenant_id}"}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    tenant_id = request.headers.get('X-Tenant-ID')
    username = data.get('username')
    return jsonify({"message": f"User {username} registered for tenant: {tenant_id}"}), 201
