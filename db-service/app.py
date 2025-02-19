import requests
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from werkzeug.exceptions import MethodNotAllowed, HTTPException
from models import Board, Thread
from common.db_utils import get_tenant_db_url
from common.error_handlers import (
    unexpected_error_handler,
    method_not_allowed_handler,
    http_exception_handler,
    bad_request_handler,
    service_unavailable_handler,
    log_exception
)
from extensions import db, cache
from routes import db_bp

migrate = Migrate()

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config['SWAGGER'] = {
        'version': 1,
        'title': 'Database Service'
    }

    db.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

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
                db_url = get_tenant_db_url(tenant_id, app.config["JWT_SECRET_KEY"])
                app.config['SQLALCHEMY_DATABASE_URI'] = db_url
                app.logger.info(f"Database URL set for tenant {tenant_id}")
            except Exception as e:
                app.logger.error(f"Failed to fetch DB URL for tenant {tenant_id}: {str(e)}")
                return {'error': str(e)}, 500

    return app

def register_error_handlers(app):
    """Register custom error handlers for the application."""
    app.register_error_handler(ValueError, bad_request_handler)
    app.register_error_handler(requests.exceptions.ConnectionError, service_unavailable_handler)
    app.register_error_handler(MethodNotAllowed, method_not_allowed_handler)
    app.register_error_handler(HTTPException, http_exception_handler)
    app.register_error_handler(Exception, unexpected_error_handler)

    # Log any unhandled exceptions
    app.register_error_handler(Exception, log_exception)

def validation_error_handler(err):
    """Handle Marshmallow validation errors."""
    return {"error": err.messages}, 400

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003)
