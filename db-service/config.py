import os
import requests

class Config:
    """Base config class for db-service."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://nba_user:nba_password@nba-db:5432/nba_db'  # Temporary hardcoded URL
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
