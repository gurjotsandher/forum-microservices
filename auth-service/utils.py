import jwt
import datetime

def generate_token(user_id, secret_key):
    return jwt.encode(
        {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        secret_key,
        algorithm="HS256"
    )
