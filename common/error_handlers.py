import traceback
from flask import current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError
import jwt

def method_not_allowed_handler(e):
    response = {
        "error": "Method Not Allowed",
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

def unexpected_error_handler(e):
    response = {
        "error": f"Internal Server Error: {str(e)}",
        "message": "Something went wrong on our end."
    }
    return jsonify(response), 500

def service_unavailable_handler(e):
    response = {
        "error": "Service Unavailable",
        "message": str(e)
    }
    return jsonify(response), 503

def bad_request_handler(e):
    response = {
        "error": "Bad Request",
        "message": str(e)
    }
    return jsonify(response), 400

def key_error_handler(e):
    response = {
        "error": "Key Error",
        "message": f"Missing or invalid key: {str(e)}"
    }
    return jsonify(response), 400

def value_error_handler(e):
    response = {
        "error": "Value Error",
        "message": f"Invalid value: {str(e)}"
    }
    return jsonify(response), 400

def database_error_handler(e):
    response = {
        "error": "Database Error",
        "message": "A database error occurred. Please try again later."
    }
    return jsonify(response), 500

def token_expired_handler(e):
    response = {
        "error": "Token Expired",
        "message": "Your token has expired. Please log in again."
    }
    return jsonify(response), 401

def invalid_token_handler(e):
    response = {
        "error": "Invalid Token",
        "message": "The provided token is invalid. Please log in again."
    }
    return jsonify(response), 401
