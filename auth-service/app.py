from flask import Flask
from routes import auth_bp  # Import the routes from routes.py

app = Flask(__name__)

# Register the authentication routes
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == "__main__":
    app.run(port=5001, debug=True)
