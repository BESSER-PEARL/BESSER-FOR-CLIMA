import time
from typing import Dict

import jwt
from decouple import config

# this should not be here, but rather hidden in the config
JWT_SECRET = "" #config("secret")
JWT_ALGORITHM = "HS256" #config("algorithm")


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 1800
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
    
# Function to refresh a token
def refresh_jwt(current_token):
    try:
        # Decode the current token without verifying expiration
        payload = jwt.decode(current_token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
        return sign_jwt(payload["user_id"])
        # Remove 'exp' field and add a new expiration time
    except jwt.InvalidTokenError:
        # Handle the case where the token is invalid
        return None