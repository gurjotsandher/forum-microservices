import requests
from common.auth_utils import verify_token
from extensions import cache


def get_tenant_db_url(tenant_id, secret_key=None):
    """Fetch the database URL for a tenant from config-service."""
    config_service_url = f"http://config-service:5002/config/get-config/{tenant_id}"

    # Check if cached
    cache_key = f"db_url_{tenant_id}"
    cache_data = cache.get(cache_key)
    if cache_data:
        payload = verify_token(cache_data['database_url_hash'], secret_key)
        return payload['database_url']

    # Send GET request to fetch config from config-service
    response = requests.get(config_service_url)
    if response.status_code == 200:
        config_data = response.json()
        cache.set(f"db_url_{tenant_id}", config_data)
        payload = verify_token(config_data['database_url_hash'], secret_key)
        return payload['database_url']
    raise Exception(f"Failed to fetch config for tenant {tenant_id}. Status Code: {response.status_code}")
