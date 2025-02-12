from flask import Flask, request, jsonify
from routes import handle_request
import config
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

@app.route("/<service>/<path:endpoint>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def gateway(service, endpoint):
    """
    Main gateway route to forward requests to microservices.
    - service: Microservice name (e.g., auth-service, post-service)
    - endpoint: The specific endpoint within that service
    """
    tenant_id = request.headers.get("X-Tenant-ID")

    if not tenant_id:
        return jsonify({"error": "Tenant ID is required"}), 400

    try:
        response = handle_request(service, endpoint, tenant_id, request)
        logger.info(f"Response from {service}: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error forwarding request to {service}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.API_GATEWAY_PORT, debug=True)
