from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, TypedDict
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from database.db import query as d1_query
import os

# Google OAuth Client ID - set in environment variables
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
DEV_TOKEN = os.environ.get("DEV_TOKEN")

class Role(str, Enum):
    ADMIN = 'admin'
    TRUSTED = 'trusted'
    USER = 'user'

    @classmethod
    def from_str(cls, value: str) -> 'Optional[Role]':
        try:
            return cls(value)
        except ValueError:
            return None

class User(TypedDict):
    email: str
    role: Role

def get_permission(auth_token: str):
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
        return 'dev', Role.ADMIN

    # Verify Google OAuth2 token
    # Source: https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.id_token.html
    info = id_token.verify_oauth2_token(token, google_auth_requests.Request(), CLIENT_ID) # pyright: ignore[reportUnknownMemberType]
    email: str = info.get('email', '')

    # Look up role in D1
    result = d1_query('SELECT type FROM perms WHERE email = ?', [email])
    role = Role.from_str(result[0]['type'])

    if not role:
        return email, Role.USER
    else:
        return email, role


def requires_roles(*auth_roles: str):
    ''' Decorator for role based access control

        Source: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/

        Returns:
            decorator: RBAC decorator
    '''
    def decorator(f: Callable[..., Any]):
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any):
            # Get Authorization header from request
            token = request.headers.get("Authorization", None)

            if not token:
                return jsonify({'error': 'No token found.'}), 401
            
            try:
                email, role = get_permission(token)
            except Exception as e:
                return jsonify({'error': str(e)}), 401

            # Check for roles
            if role not in auth_roles:
                return jsonify({'error': 'Unauthorized user.'}), 403
            
            # Pass current user info to route parameters
            user = User(email=email, role=Role.ADMIN) # pyright: ignore[reportUnusedVariable]
            # kwargs['current_user'] = user
            
            return f(*args, **kwargs)
        return decorated
    return decorator
