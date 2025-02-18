import os

class Config:
    """Base config class."""
    # JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    DB_SERVICE_URL = os.getenv("DB_SERVICE_URL")

