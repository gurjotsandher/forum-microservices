from flask import Flask
from werkzeug.exceptions import MethodNotAllowed, HTTPException
from routes import auth_bp
from common.error_handlers import method_not_allowed_handler, http_exception_handler, unexpected_error_handler
from common.logger import setup_logger

app = Flask(__name__)
app.logger = setup_logger("auth-service")

# Register the shared error handlers
app.register_error_handler(MethodNotAllowed, method_not_allowed_handler)
app.register_error_handler(HTTPException, http_exception_handler)
app.register_error_handler(Exception, lambda e: unexpected_error_handler(e, app))

# Register the authentication routes
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == "__main__":
    app.run(port=5001, debug=True)
