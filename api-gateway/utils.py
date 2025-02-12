def log_request(service, endpoint, tenant_id):
    """
    Logs the incoming request details.
    """
    print(f"Tenant: {tenant_id} | Service: {service} | Endpoint: {endpoint}")
