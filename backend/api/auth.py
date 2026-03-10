from functools import wraps
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from database.admin import get_role
import sqlite3
import os

# Google OAuth Client ID - set in environment variables
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
DEV_TOKEN = os.environ.get("DEV_TOKEN")

# Database - path relative to this file
AUTH = os.path.join(os.path.dirname(__file__), '..', 'database', 'pantry.db')

ROLES = ['admin', 'trusted', 'user']

def get_permission(auth_token):
    ''' Verify auth_token and extract information from auth_token. 
        After, check for the role of the user

        Returns:
            (email, role) tuple if valid
            ('dev', 'admin') if using dev token
            ('', 'user') if current user is not authorized for admin or trusted
    '''
    # Check for token header
    if not auth_token or not auth_token.startswith('Bearer '):
        raise ValueError('Invalid token format')
    
    # Extract token (removing header)
    token = auth_token.split(' ', 1)[1]

    # Dev token bypass
    if DEV_TOKEN and token == DEV_TOKEN:
        return 'dev', 'admin'

    # Verify Google OAuth2 token
    # Source: https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.id_token.html
    info = id_token.verify_oauth2_token(token, google_auth_requests.Request(), CLIENT_ID)
    email = info.get('email', '')

    connection = sqlite3.connect(AUTH)
    cursor = connection.cursor()

    role = get_role(cursor, email)
    connection.close()

    # If user's email is not in authorized user table, they are just 'user'
    if role == []:
        return email, 'user'
    else:
        return email, role


def requires_roles(*auth_roles):
    ''' Decorator for role based access control

        Source: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/

        Returns:
            decorator: RBAC decorator
    '''
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get Authorization header from request
            token = request.headers.get("Authorization", None)

            if not token:
                return jsonify({'error': 'No token found.'}), 401
            
            try:
                email, role = get_permission(token)
            except Exception:
                return jsonify({'error': 'Invalid or expired token.'}), 401

            # Check for roles
            if role not in auth_roles:
                return jsonify({'error': 'Unauthorized user.'}), 403
            
            # Pass current user info to route parameters
            kwargs['current_user'] = {'email': email, 'role': role}
            
            return f(*args, **kwargs)
        return decorated
    return decorator