import requests
from extensions import cache


def get_tenant_db_url(tenant_id):
    """Fetch the database URL for a tenant from config-service."""
    config_service_url = f"http://config-service:5002/config/get-config/{tenant_id}"

    # Send GET request to fetch config from config-service
    response = requests.get(config_service_url)
    if response.status_code == 200:
        config_data = response.json()
        return config_data.get("database_url")
    else:
        raise Exception(f"Failed to fetch config for tenant {tenant_id}. Status Code: {response.status_code}")
