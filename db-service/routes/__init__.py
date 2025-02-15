from flask import Blueprint, jsonify
from .user_routes import user_bp
from .board_routes import board_bp
from .thread_routes import thread_bp

db_bp = Blueprint('db', __name__)

# Health check endpoint
@db_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for db-service."""
    return jsonify({"status": "ok"}), 200

# Register all blueprints
db_bp.register_blueprint(user_bp, url_prefix='/user')
db_bp.register_blueprint(board_bp, url_prefix='/board')
db_bp.register_blueprint(thread_bp, url_prefix='/thread')
