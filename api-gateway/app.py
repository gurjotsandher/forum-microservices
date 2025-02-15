import requests
from flask import Flask
from werkzeug.exceptions import MethodNotAllowed, HTTPException
from routes import gateway_bp
from common.error_handlers import method_not_allowed_handler, http_exception_handler, unexpected_error_handler, \
    service_unavailable_handler, bad_request_handler

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Register the Blueprint
    app.register_blueprint(gateway_bp, url_prefix="/")

    # Register shared error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    """Register shared error handlers for the application."""
    app.register_error_handler(ValueError, bad_request_handler)
    app.register_error_handler(requests.exceptions.ConnectionError, service_unavailable_handler)
    app.register_error_handler(MethodNotAllowed, method_not_allowed_handler)
    app.register_error_handler(HTTPException, http_exception_handler)
    app.register_error_handler(Exception, unexpected_error_handler)

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
