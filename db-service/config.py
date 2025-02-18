import os

class Config:
    """Base config class for db-service."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("MIGRATION_URI")
    CACHE_TYPE = os.getenv("CACHE_TYPE") # "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
