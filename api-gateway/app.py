import requests
from flask import Flask
from werkzeug.exceptions import MethodNotAllowed, HTTPException
from routes import gateway_bp
from common.error_handlers import method_not_allowed_handler, http_exception_handler, unexpected_error_handler, \
    service_unavailable_handler, bad_request_handler
from common.logger import setup_logger

app = Flask(__name__)
app.logger = setup_logger("api-gateway")

# Register the Blueprint
app.register_blueprint(gateway_bp, url_prefix="/", logger=app.logger)

# Register shared error handlers
app.register_error_handler(ValueError, bad_request_handler)
app.register_error_handler(requests.exceptions.ConnectionError, service_unavailable_handler)
app.register_error_handler(MethodNotAllowed, method_not_allowed_handler)
app.register_error_handler(HTTPException, http_exception_handler)
app.register_error_handler(Exception, lambda e: unexpected_error_handler(e, app))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
