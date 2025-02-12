import requests
from flask import Response, request
import config
import logging

logger = logging.getLogger(__name__)

def handle_request(service, endpoint, tenant_id, client_request):
    """
    Forward the request to the appropriate microservice.
    """
    if service not in config.SERVICE_MAP:
        logger.warning(f"Service {service} not found in SERVICE_MAP")
        return {"error": "Service not found"}, 404

    url = f"{config.SERVICE_MAP[service]}/{endpoint}"
    headers = {
        key: value for key, value in client_request.headers if key != "Host"
    }
    headers["X-Tenant-ID"] = tenant_id  # Ensure tenant ID is forwarded
    logger.info(f"Forwarding request to {service} at {url}")

    response = requests.request(
        method=client_request.method,
        url=url,
        headers=headers,
        data=client_request.get_data(),
        params=client_request.args,
    )

    logger.info(f"Received response from {service} with status code: {response.status_code}")
    return Response(response.content, status=response.status_code, headers=dict(response.headers))
