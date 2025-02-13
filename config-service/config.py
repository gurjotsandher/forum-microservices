import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@config-db:5432/config_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key_here")

