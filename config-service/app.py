from flask import Flask
from flask_migrate import Migrate
from config import Config
from extensions import db, cache
from routes import config_bp
import logging

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Initialize extensions
db.init_app(app)
cache.init_app(app)
migrate = Migrate(app, db)

# Register blueprint
app.register_blueprint(config_bp, url_prefix='/config')

# Cache test to check if Redis is accessible
@app.route("/test-cache")
def test_cache():
    cache.set("test_key", "This is a test value", timeout=300)
    cached_value = cache.get("test_key")
    if cached_value:
        return f"Cache works! Value: {cached_value}", 200
    return "Cache not working.", 500

@app.route('/health', methods=['GET'])
def health():
    # Perform any basic checks if needed
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
