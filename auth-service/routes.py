from flask import Blueprint, request, jsonify
from common.utils import validate_tenant_id

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET"])
def login():
    try:
        tenant_id = validate_tenant_id(request.headers)
        return jsonify({"message": f"Mock login success for tenant: {tenant_id}"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    tenant_id = request.headers.get('X-Tenant-ID')
    username = data.get('username')
    return jsonify({"message": f"User {username} registered for tenant: {tenant_id}"}), 201
