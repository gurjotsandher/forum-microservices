from flask import Blueprint, request, jsonify
from extensions import db, cache
from models import TenantConfig
from auth import token_required
from common.auth_utils import generate_token, verify_token
from config import Config

config_bp = Blueprint("config", __name__)

@config_bp.route("/get-config/<tenant_id>", methods=["GET"])
def get_config(tenant_id):
    # Check if the configuration is cached
    print(f"tenant id => {tenant_id}")
    cached_config = cache.get(tenant_id)
    if cached_config:
        return jsonify(cached_config), 200

    # Query the tenant configuration from the database
    db_response = TenantConfig.query.filter_by(tenant_id=tenant_id).first()

    if not db_response:
        return jsonify({"error": "Configuration not found"}), 404

    # Prepare the response with the relevant fields
    response = {
        "tenant_id": db_response.tenant_id,
        "database_url_hash": db_response.database_url_hash,
        "feature_flags": db_response.feature_flags
    }

    # Cache the response for 5 minutes
    cache.set(tenant_id, response, timeout=300)

    return jsonify(response), 200


@config_bp.route("/add-config", methods=["POST"])
@token_required
def add_config():
    data = request.get_json()
    # Ensure required fields are present
    if not data or "tenant_id" not in data or "database_url" not in data:
        return jsonify({"error": "Invalid request"}), 400  # 400 Bad Request

    # Check if the tenant already exists
    existing_config = TenantConfig.query.filter_by(tenant_id=data["tenant_id"]).first()
    if existing_config:
        return jsonify({"error": f"Configuration for {data['tenant_id']} already exists"}), 409  # 409 Conflict

    try:
        payload = {
            "database_url": data["database_url"]
        }
        database_url_hash = generate_token(Config.JWT_SECRET_KEY, payload)
        # Create the new tenant configuration
        config = TenantConfig(
            tenant_id=data["tenant_id"],
            database_url_hash=database_url_hash,
            feature_flags=data.get("feature_flags")
        )
        db.session.add(config)
        db.session.commit()
        cache.delete(data["tenant_id"])
        return jsonify({"message": f"Configuration for {data['tenant_id']} added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@config_bp.route("/update-config/<tenant_id>", methods=["PUT"])
@token_required
def update_config(tenant_id):
    data = request.get_json()

    # Fetch the tenant config from the database
    config = TenantConfig.query.filter_by(tenant_id=tenant_id).first()
    if not config:
        return jsonify({"error": "Configuration not found"}), 404

    # Update the relevant fields in the tenant config
    config.database_url = data.get("database_url_hash", config.database_url)  # Update database_url
    config.feature_flags = data.get("feature_flags", config.feature_flags)  # Update feature_flags

    # Commit the changes to the database
    db.session.commit()

    # Clear the cache for the tenant configuration
    cache.delete(tenant_id)

    return jsonify({"message": f"Configuration for {tenant_id} updated successfully"}), 200

@config_bp.route("/delete-config/<tenant_id>", methods=["DELETE"])
@token_required
def delete_config(tenant_id):
    # Fetch the tenant config from the database
    config = TenantConfig.query.filter_by(tenant_id=tenant_id).first()
    if not config:
        return jsonify({"error": "Configuration not found"}), 404

    # Delete the tenant configuration from the database
    db.session.delete(config)
    db.session.commit()

    # Clear the cache for the tenant configuration
    cache.delete(tenant_id)

    return jsonify({"message": f"Configuration for {tenant_id} deleted successfully"}), 204

# Cache test to check if Redis is accessible
@config_bp.route("/test-cache")
def test_cache():
    cache.set("test_key", "This is a test value", timeout=300)
    cached_value = cache.get("test_key")
    if cached_value:
        return f"Cache works! Value: {cached_value}", 200
    return "Cache not working.", 500

@config_bp.route('/health', methods=['GET'])
def health():
    # Perform any basic checks if needed
    return "OK", 200
