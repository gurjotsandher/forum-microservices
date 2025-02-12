import logging

def setup_logger(service_name):
    """
    Set up and return a logger with a consistent format and level.
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger

def log_request(logger, service, endpoint, tenant_id):
    """
    Logs the incoming request details using the provided logger.
    """
    logger.info(f"Tenant: {tenant_id} | Service: {service} | Endpoint: {endpoint}")
