# import debugpy
from dotenv import load_dotenv
# import os
from flask import Flask
from werkzeug.exceptions import MethodNotAllowed, HTTPException
from routes import auth_bp
from common.error_handlers import method_not_allowed_handler, http_exception_handler, unexpected_error_handler
from common.logger import setup_logger

app = Flask(__name__)
app.logger = setup_logger("auth-service")

load_dotenv()

# Register the shared error handlers
app.register_error_handler(MethodNotAllowed, method_not_allowed_handler)
app.register_error_handler(HTTPException, http_exception_handler)
app.register_error_handler(Exception, lambda e: unexpected_error_handler(e, app))

# Register the authentication routes
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/health', methods=['GET'])
def health():
    # Perform any basic checks if needed
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
