API_GATEWAY_PORT = 5000

# Microservices and their base URLs
SERVICE_MAP = {
    "auth": "http://auth-service:5001/auth",
    "config": "http://config-service:5002/config",
    "db": "http://db-service:5003/db",
    "post": "http://post-service:5004/post"
}
