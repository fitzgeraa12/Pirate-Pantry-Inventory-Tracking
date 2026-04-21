# Returns all users in the table
from typing import Optional
import os
import sys

sys.path.append(os.path.abspath('/workspaces/Pirate-Pantry-Inventory-Tracking/backend/api'))
from auth import Role
from db import query, rows_to_list


def view_all():
    rows = query('SELECT * FROM perms')
    return (rows)

# Returns all admin users in the table
def view_admins():
    rows = query("SELECT * FROM perms WHERE type == ?", [Role.ADMIN])
    return (rows)

# Returns all trusted users in the table
def view_trusted():
    rows = query("SELECT * FROM perms WHERE type == ?", [Role.TRUSTED])
    return (rows)

# Returns true if the email is a trusted or admin user
def in_table(email: str):
    rows = query('SELECT * FROM perms WHERE email == ?', [email])
    if len((rows)) > 0:
        return True
    return False

# Returns true if the user is an admin, false if they're trusted
def is_admin(email: str):
    rows = query("SELECT * FROM perms WHERE email == ? AND type == ?", [email, Role.ADMIN])
    if len((rows)) > 0:
        return True
    return False

# Returns the role of the user, [] if the user is not in the table
def get_role(email: str) -> Optional[str]:
    rows = query('SELECT type FROM perms WHERE email == ?', [email])
    if len(rows) > 0:
        return (rows)[0][0]
    return None

# Adds a new user to the table. Checks for if the user is an admin comes from the API
def add_user(new_email: str, ty: str):
    query('INSERT INTO perms VALUES (?, ?)', [new_email, ty])

# Removes a user from the table. Admin users can only be removed if there's more than one admin remaining
def remove_user(email: str):
    if in_table(email):
        if is_admin(email): 
            if len(view_admins()) <= 1:
                return "Must have at least one admin"
        query('DELETE FROM perms WHERE email == ?', [email])
        return True
    else:
        return "User not found"
