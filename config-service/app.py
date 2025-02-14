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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
