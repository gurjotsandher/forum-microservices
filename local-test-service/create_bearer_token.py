import jwt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the secret key from the environment variable (ensure it exists in your .env file)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    print("Error: JWT_SECRET_KEY not found in .env file.")
else:
    # Encode the payload with the secret key and the HS256 algorithm
    payload = {"user": "test_user"}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    print(f"Bearer {token}")
