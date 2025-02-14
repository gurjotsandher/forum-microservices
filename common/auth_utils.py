import jwt
import datetime

def generate_token(user_id, secret_key, expiration_hours=1):
    """
    Generate a JWT token for a given user.
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def verify_token(token, secret_key):
    """
    Verify a JWT token and return the decoded payload.
    Raises jwt.ExpiredSignatureError if the token has expired.
    Raises jwt.InvalidTokenError for any other validation error.
    """
    return jwt.decode(token, secret_key, algorithms=["HS256"])