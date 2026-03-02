from functools import wraps
from flask import request, jsonify
from google.oauth2 import id_token        # Add to README, need pip install google-auth
from google.auth.transport import requests as google_auth_requests
import database
import sqlite3

# Google OAuth Client ID (from frontend)
CLIENT_ID = "391677624577-24ihed14clpj1d3ioumsq08aeagrj30n.apps.googleusercontent.com";

# Database
DB = '/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db'

ROLES = ['admin', 'trusted', 'user']
    
def get_permission(auth_token):
    ''' Verify auth_token and extract information from auth_token. 
        After, check for the role of the user

        Returns:
            email, role if valid
            'user' if current user is not authorized for admin or trusted
    '''
    # Check for token header
    if not auth_token.startswith('Bearer '):
        raise ValueError('Invalid token format')
    
    # Extract token (removing header)
    token = auth_token.split(' ', 1)[1]

    # Source: https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.id_token.html#:~:text=To%20parse%20and%20verify%20an,is%20available%20as%20verify_token()%20.&text=Verifies%20an%20ID%20token%20and%20returns%20the%20decoded%20token.
    # Verify an ID Token issued by Google’s OAuth 2.0 authorization
    info = id_token.verify_oauth2_token(token, google_auth_requests.Request(), CLIENT_ID)
    email = info.get('email', '')

    connection = sqlite3.connect(DB)
    cursor = connection.cursor()

    # Will need to confirm with database method
    role = database.get_role(cursor, email) # Check for user roles from authorized user table
    connection.close()

    # If user's email is not in authorized user table, they are just 'user'
    if role is []:
        return 'user'
    else:
        return email, role 


def requires_roles(*auth_roles):
    def decorator(f):
        ''' Decorator for role base access control

            Source: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/ 

            Returns:
                decorator: RBAC decorator
        '''
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get Authorization header from request
            token = request.headers.get("Authorization", None)

            # No token means unauthorized
            if not token:
                return jsonify({'error': 'Invalid or expired token.'}), 401
            
            try:
                # Verify token and get user email and role
                email, role = get_permission(token)
            except Exception:
                return jsonify({'error': 'Invalid or expired token.'}), 401

            # Check for roles
            if role not in auth_roles:
                return jsonify({'error': 'Unauthorized User.'}), 403
            
            # Put current user info to route parameters
            kwargs['current_user'] = {'email': email, 'role': role}
            
            return f(*args, **kwargs)
        return decorated
    return decorator