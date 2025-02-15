import logging
from flask import current_app, jsonify


def get_dynamic_logger():
    # Dynamically set the logger name based on the application context
    # You can use current_app.name or any other relevant information
    logger_name = current_app.name if hasattr(current_app, 'name') else 'unknown_service'
    logger = logging.getLogger(logger_name)
    return logger


def method_not_allowed_handler(e):
    logger = get_dynamic_logger()
    logger.warning(f"Method Not Allowed: {str(e)}")  # Log the error context

    response = {
        "error": "Method Not Allowed",
        "message": "The requested method is not allowed for this endpoint."
    }
    return jsonify(response), 405


def http_exception_handler(e):
    logger = get_dynamic_logger()
    logger.error(f"HTTP Exception: {str(e)}")  # Log the error details

    response = {
        "error": e.name,
        "code": e.code,
        "message": str(e.description)
    }
    return jsonify(response), e.code


def unexpected_error_handler(e):
    logger = get_dynamic_logger()
    logger.critical(f"Unexpected Error: {str(e)}")  # Log the unexpected error

    response = {
        "error": f"Internal Server Error: {str(e)}",
        "message": "Something went wrong on our end."
    }
    return jsonify(response), 500


def service_unavailable_handler(e):
    logger = get_dynamic_logger()
    logger.error(f"Service Unavailable: {str(e)}")  # Log service availability issues

    response = {
        "error": "Service Unavailable",
        "message": str(e)
    }
    return jsonify(response), 503


def bad_request_handler(e):
    logger = get_dynamic_logger()
    logger.warning(f"Bad Request: {str(e)}")  # Log invalid request error

    response = {
        "error": "Bad Request",
        "message": str(e)
    }
    return jsonify(response), 400
