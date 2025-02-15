import logging

def setup_logger(name):
    """Deprecated use dyanmic logger in error_handler.py"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler to log to a file
    file_handler = logging.FileHandler(f'{name}.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler to log to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Basic log levels
def log_debug(logger, message):
    logger.debug(message)

def log_info(logger, message):
    logger.info(message)

def log_warning(logger, message):
    logger.warning(message)

def log_error(logger, message):
    logger.error(message)

def log_critical(logger, message):
    logger.critical(message)

# Error logging with stack trace
def log_error_with_stack_trace(logger, exception):
    logger.error(f"Exception occurred: {str(exception)}", exc_info=True)

# Request and response logging
def log_request(logger, service, endpoint, tenant_id, method, headers=None, request_data=None):
    logger.info(f"Tenant: {tenant_id} | Service: {service} | Endpoint: {endpoint} | Method: {method} "
                f"| Headers: {headers} | Data: {request_data}")

def log_response(logger, service, endpoint, tenant_id, status_code, response_data=None):
    logger.info(f"Tenant: {tenant_id} | Service: {service} | Endpoint: {endpoint} | Status Code: {status_code} "
                f"| Response Data: {response_data}")

# Health check logging
def log_health_check(logger, service, tenant_id, status):
    logger.info(f"Health check for {service} | Tenant: {tenant_id} | Status: {status}")

# Business-specific event logging
def log_user_action(logger, user_id, action, details=None):
    logger.info(f"User ID: {user_id} | Action: {action} | Details: {details}")
