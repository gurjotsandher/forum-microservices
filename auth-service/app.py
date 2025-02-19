from flask import Flask
from werkzeug.exceptions import MethodNotAllowed, HTTPException
from common.error_handlers import (
    method_not_allowed_handler,
    http_exception_handler,
    unexpected_error_handler,
    # key_error_handler,
    # value_error_handler,
    # database_error_handler,
    # token_expired_handler,
    # invalid_token_handler
)
from extensions import db
# Application-Specific Imports
from routes import auth_bp

# Create Flask app using factory pattern
def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Register error handlers
    register_error_handlers(app)

    # Register authentication routes
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

# Register error handlers
def register_error_handlers(app):
    # Specific handlers for predictable exceptions
    # app.register_error_handler(KeyError, key_error_handler)
    # app.register_error_handler(ValueError, value_error_handler)
    # app.register_error_handler(SQLAlchemyError, database_error_handler)  # Now this works
    # app.register_error_handler(jwt.ExpiredSignatureError, token_expired_handler)
    # app.register_error_handler(jwt.InvalidTokenError, invalid_token_handler)

    # General handlers for broader coverage
    app.register_error_handler(MethodNotAllowed, method_not_allowed_handler)
    app.register_error_handler(HTTPException, http_exception_handler)
    app.register_error_handler(Exception, lambda e: unexpected_error_handler(e))

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
