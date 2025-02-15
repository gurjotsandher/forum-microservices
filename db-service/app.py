from flask import Flask, request, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import MethodNotAllowed, HTTPException
import jwt
from extensions import db, cache
from routes import db_bp
from marshmallow import ValidationError
from common.error_handlers import (
    # key_error_handler,
    # value_error_handler,
    unexpected_error_handler,
    method_not_allowed_handler,
    # database_error_handler,
    # token_expired_handler,
    # invalid_token_handler,
    http_exception_handler
)
from common.db_utils import get_tenant_db_url  # Corrected import

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    cache.init_app(app)

    migrate = Migrate(app, db)

    # Register routes
    app.register_blueprint(db_bp, url_prefix='/db')

    # Register error handlers
    register_error_handlers(app)

    # Before request hook to dynamically set the DB URL
    @app.before_request
    def set_db_url():
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                db_url = get_tenant_db_url(tenant_id)
                app.config['SQLALCHEMY_DATABASE_URI'] = db_url
            except Exception as e:
                return {'error': str(e)}, 500

    return app

def register_error_handlers(app):
    """Register custom error handlers for the application."""
    # Specific handlers for predictable exceptions
    # app.register_error_handler(KeyError, key_error_handler)
    # app.register_error_handler(ValueError, value_error_handler)
    # app.register_error_handler(SQLAlchemyError, database_error_handler)  # Now this works
    # app.register_error_handler(jwt.ExpiredSignatureError, token_expired_handler)
    # app.register_error_handler(jwt.InvalidTokenError, invalid_token_handler)

    # General handlers for broader coverage
    app.register_error_handler(MethodNotAllowed, method_not_allowed_handler)
    app.register_error_handler(HTTPException, http_exception_handler)
    app.register_error_handler(Exception, unexpected_error_handler)  # No need for lambda

def validation_error_handler(err):
    """Handle Marshmallow validation errors."""
    return {"error": err.messages}, 400

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003)
