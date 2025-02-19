import requests
from common.auth_utils import verify_token
from extensions import cache


def get_tenant_db_url(tenant_id, secret_key=None):
    """Fetch the database URL for a tenant from config-service."""
    config_service_url = f"http://config-service:5002/config/get-config/{tenant_id}"

    # Send GET request to fetch config from config-service
    response = requests.get(config_service_url)
    if response.status_code == 200:
        config_data = response.json()
        payload = verify_token(config_data['database_url_hash'], secret_key)
        return payload['database_url']
    raise Exception(f"Failed to fetch config for tenant {tenant_id}. Status Code: {response.status_code}")
