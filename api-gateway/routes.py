import requests
from flask import Blueprint, Response, request
import config
from common.logger import log_request
from common.utils import validate_tenant_id
from flask import current_app

gateway_bp = Blueprint('gateway', __name__)

@gateway_bp.route("/<service>/<path:endpoint>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def gateway(service, endpoint):
    tenant_id = validate_tenant_id(request.headers)
    log_request(current_app.logger, service, endpoint, tenant_id)  # Use current_app.logger
    return handle_request(service, endpoint, tenant_id, request)

@gateway_bp.route('/health', methods=['GET'])
def health():
    # Perform any basic checks if needed
    return "OK", 200

def handle_request(service, endpoint, tenant_id, client_request):
    if service not in config.SERVICE_MAP:
        raise ValueError(f"Service '{service}' not found in SERVICE_MAP")

    url = f"{config.SERVICE_MAP[service]}/{endpoint}"
    headers = {key: value for key, value in client_request.headers if key.lower() != "host"}
    headers["X-Tenant-ID"] = tenant_id

    try:
        response = requests.request(
            method=client_request.method,
            url=url,
            headers=headers,
            data=client_request.get_data(),
            params=client_request.args,
            timeout=5
        )
        return Response(response.content, status=response.status_code, headers=dict(response.headers))

    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError(f"Could not connect to {service}")

    except requests.exceptions.Timeout:
        raise requests.exceptions.Timeout(f"Request to {service} timed out")
