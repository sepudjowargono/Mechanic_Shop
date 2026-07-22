import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "this-is-my-super-super-secret-key"

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),  # Token expires in 1 hour
        'iat': datetime.now(timezone.utc),  # Issued at time
        'sub': str(customer_id),  # Subject of the token (user ID)
        'role': 'customer' # Role of user, can be used for role-based access control
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') # hashing algorithm used to sign the token (scramble and protect the payload data)
    
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "message": "You must be logged in to access this."
            }), 401

        header_parts = auth_header.split()

        if len(header_parts) != 2 or header_parts[0].lower() != "bearer":
            return jsonify({
                "message": "Authorization header must use Bearer token format."
            }), 401

        token = header_parts[1]

        try:
            data = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=["HS256"]
            )

            if data.get("role") != "customer":
                return jsonify({
                    "message": "Invalid role for this token!"
                }), 403

            customer_id = int(data["sub"])

        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired!"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid token!"
            }), 401

        except (KeyError, TypeError, ValueError):
            return jsonify({
                "message": "Invalid token payload!"
            }), 401

        return f(customer_id, *args, **kwargs)

    return decorated

def encode_mechanic_token(mechanic_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),  # Token expires in 1 hour
        'iat': datetime.now(timezone.utc),  # Issued at time
        'sub': str(mechanic_id),  # Subject of the token (user ID)
        'role': 'mechanic' # Role of user, can be used for role-based access control
    }
    
    mechanic_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') # hashing algorithm used to sign the token (scramble and protect the payload data)
    
    return mechanic_token

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "message": "You must be logged in to access this."
            }), 401

        header_parts = auth_header.split()

        if len(header_parts) != 2 or header_parts[0].lower() != "bearer":
            return jsonify({
                "message": "Authorization header must use Bearer token format."
            }), 401

        mechanic_token = header_parts[1]

        try:
            data = jwt.decode(
                mechanic_token,
                SECRET_KEY,
                algorithms=["HS256"]
            )

            if data.get("role") != "mechanic":
                return jsonify({
                    "message": "Invalid role for this token!"
                }), 403

            mechanic_id = int(data["sub"])

        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired!"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid token!"
            }), 401

        except (KeyError, TypeError, ValueError):
            return jsonify({
                "message": "Invalid token payload!"
            }), 401

        return f(mechanic_id, *args, **kwargs)

    return decorated