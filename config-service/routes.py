from flask import Blueprint, request, jsonify
from extensions import db, cache
from models import TenantConfig
from auth import token_required

config_bp = Blueprint("config", __name__)

@config_bp.route("/get-config/<tenant_id>", methods=["GET"])
def get_config(tenant_id):
    cached_config = cache.get(tenant_id)
    if cached_config:
        return jsonify(cached_config), 200

    config = TenantConfig.query.filter_by(tenant_id=tenant_id).first()
    if not config:
        return jsonify({"error": "Configuration not found"}), 404

    response = {
        "tenant_id": config.tenant_id,
        "db_url": config.db_url,
        "feature_flags": config.feature_flags
    }
    cache.set(tenant_id, response, timeout=300)
    return jsonify(response), 200

@config_bp.route("/add-config", methods=["POST"])
@token_required
def add_config():
    data = request.get_json()
    if not data or "tenant_id" not in data or "db_url" not in data:
        return jsonify({"error": "Invalid request"}), 400

    existing_config = TenantConfig.query.filter_by(tenant_id=data["tenant_id"]).first()
    if existing_config:
        return jsonify({"error": f"Configuration for {data['tenant_id']} already exists"}), 409  # 409 Conflict

    try:
        config = TenantConfig(tenant_id=data["tenant_id"], db_url=data["db_url"], feature_flags=data.get("feature_flags"))
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
    config = TenantConfig.query.filter_by(tenant_id=tenant_id).first()
    if not config:
        return jsonify({"error": "Configuration not found"}), 404

    config.db_url = data.get("db_url", config.db_url)
    config.feature_flags = data.get("feature_flags", config.feature_flags)
    db.session.commit()
    cache.delete(tenant_id)
    return jsonify({"message": f"Configuration for {tenant_id} updated successfully"}), 200

@config_bp.route("/delete-config/<tenant_id>", methods=["DELETE"])
@token_required
def delete_config(tenant_id):
    config = TenantConfig.query.filter_by(tenant_id=tenant_id).first()
    if not config:
        return jsonify({"error": "Configuration not found"}), 404

    db.session.delete(config)
    db.session.commit()
    cache.delete(tenant_id)
    return jsonify({"message": f"Configuration for {tenant_id} deleted successfully"}), 200
