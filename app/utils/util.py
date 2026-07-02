import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "this-is-my-super-super-secret-key" # In a real application, this should be stored securely and not hardcoded.

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),  # Token expires in 1 hour
        'iat': datetime.now(timezone.utc),  # Issued at time
        'sub': str(customer_id)  # Subject of the token (user ID)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') # hashing algorithm used to sign the token (scramble and protect the payload data)
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            
            token = request.headers['Authorization'].split()[1]  # Assuming the token is sent as "Bearer <token>"
            
            if not token: 
                return jsonify({'message': 'Token is missing!'}), 400
            
            try:
                
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                print(data)
                customer_id = int(data['sub'])
            except jwt.ExpiredSignatureError as e:
                return jsonify({'message': 'Token has expired!'}), 400
            except jwt.InvalidTokenError as e:
                return jsonify({'message': 'Invalid token!'}), 400
            
            return f(customer_id, *args, **kwargs)
        
        else:
            return jsonify({'message': 'You must be logged in to access this.'}), 400 
        
    return decorated  
                