from flask import Blueprint, request, jsonify, Response
from common.error_handlers import get_dynamic_logger
from common.utils import validate_tenant_id
from flask import current_app
import config
import requests

gateway_bp = Blueprint('gateway', __name__)

@gateway_bp.route("/<service>/<path:endpoint>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def gateway(service, endpoint):
    logger = get_dynamic_logger()
    tenant_id = validate_tenant_id(request.headers)

    # Log the incoming request
    logger.info(f"Tenant ID: {tenant_id} | Service: {service} | Endpoint: {endpoint} - Request received")

    try:
        # Handle the request (assuming handle_request is a function you already have)
        return handle_request(service, endpoint, tenant_id, request)

    except requests.exceptions.ConnectionError as e:
        # Log error if a connection error occurs
        logger.error(f"Connection error while trying to reach service: {service}, endpoint: {endpoint} - {str(e)}")
        return jsonify({"error": "Service Unavailable", "message": str(e)}), 503

    except requests.exceptions.Timeout as e:
        # Log timeout error
        logger.warning(f"Request to service: {service}, endpoint: {endpoint} timed out - {str(e)}")
        return jsonify({"error": "Request Timeout", "message": str(e)}), 504

    except Exception as e:
        # Log unexpected errors
        logger.exception(f"Unexpected error occurred while processing request: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "Something went wrong on our end."}), 500

def handle_request(service, endpoint, tenant_id, client_request):
    logger = get_dynamic_logger()
    if service not in config.SERVICE_MAP:
        raise ValueError(f"Service '{service}' not found in SERVICE_MAP")

    url = f"{config.SERVICE_MAP[service]}/{endpoint}"
    headers = {key: value for key, value in client_request.headers if key.lower() != "host"}
    headers["X-Tenant-ID"] = tenant_id

    try:
        logger.info(f"Making request to: {url} with headers: {headers}")

        response = requests.request(
            method=client_request.method,
            url=url,
            headers=headers,
            data=client_request.get_data(),
            params=client_request.args,
            timeout=5
        )

        logger.info(f"Received response: {response.status_code} from service: {service}, endpoint: {endpoint}")
        return Response(response.content, status=response.status_code, headers=dict(response.headers))

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise e

    except requests.exceptions.Timeout as e:
        logger.warning(f"Timeout error: {str(e)}")
        raise e
