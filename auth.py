from functools import wraps
from flask import request, jsonify, abort
from google.oauth2 import id_token        # Add to README, need pip install google-auth
from google.auth.transport import requests as google_auth_requests
import database
import sqlite3

CLIENT_ID = "391677624577-24ihed14clpj1d3ioumsq08aeagrj30n.apps.googleusercontent.com";
DB = '/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db'

ROLES = ['admin', 'trusted', 'user']
    
def get_permission(auth_token):
    if not auth_token.startswith('Bearer '):
        raise ValueError('Invalid token format')
    
    token = auth_token.split(' ', 1)[1]

    info = id_token.verify_oauth2_token(token, google_auth_requests.Request(), CLIENT_ID)
    email = info.get('email', '')

    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    role = database.get_role(cursor, email)
    connection.close()

    if role is []:
        return 'user'
    else:
        return email, role 


def requires_roles(*auth_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization", None)
            if not token:
                return jsonify({'error': 'Invalid or expired token.'}), 401
            
            try:
                email, role = get_permission(token)
            except Exception:
                return jsonify({'error': 'Invalid or expired token.'}), 401

            # Check for roles
            if role not in auth_roles:
                return jsonify({'error': 'Unauthorized User.'}), 403
            
            kwargs['current_user'] = {'email': email, 'role': role}
            
            return f(*args, **kwargs)
        return decorated
    return decorator