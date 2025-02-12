from flask import jsonify

def method_not_allowed_handler(e):
    response = {
        "error": "Method not allowed",
        "message": "The requested method is not allowed for this endpoint."
    }
    return jsonify(response), 405

def http_exception_handler(e):
    response = {
        "error": e.name,
        "code": e.code,
        "message": str(e.description)
    }
    return jsonify(response), e.code

def unexpected_error_handler(e, app):
    app.logger.error(f"Unhandled exception: {e}")
    response = {
        "error": "Internal Server Error",
        "message": "Something went wrong on our end."
    }
    return jsonify(response), 500

def service_unavailable_handler(e):
    response = {
        "error": "Service unavailable",
        "message": str(e)
    }
    return jsonify(response), 503

def bad_request_handler(e):
    response = {
        "error": "Bad request",
        "message": str(e)
    }
    return jsonify(response), 400