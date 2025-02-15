import os

class Config:
    """Base config class."""
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_key")
