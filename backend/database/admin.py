import sqlite3

# Returns all users in the table
def view_all(cursor):
    cursor.execute('SELECT * FROM perms')
    return cursor.fetchall()

# Returns all admin users in the table
def view_admins(cursor):
    cursor.execute("SELECT * FROM perms WHERE type == 'admin'")
    return cursor.fetchall()

# Returns all trusted users in the table
def view_trusted(cursor):
    cursor.execute("SELECT * FROM perms WHERE type == 'trusted'")
    return cursor.fetchall()

# Returns true if the email is a trusted or admin user
def in_table(cursor, email):
    cursor.execute('SELECT * FROM perms WHERE email == ?', (email, ))
    if len(cursor.fetchall()) > 0:
        return True
    return False

# Returns true if the user is an admin, false if they're trusted
def is_admin(cursor, email):
    cursor.execute("SELECT * FROM perms WHERE email == ? AND type == 'admin'", (email, ))
    if len(cursor.fetchall()) > 0:
        return True
    return False

# Returns the role of the user, [] if the user is not in the table
def get_role(cursor, email):
    cursor.execute('SELECT type FROM perms WHERE email == ?', (email, ))
    result = cursor.fetchall()
    if len(result) > 0:
        return result[0][0]
    return []

# Adds a new user to the table. Checks for if the user is an admin comes from the API
def add_user(cursor, new_email, type):
    cursor.execute('INSERT INTO perms VALUES (?, ?)', (new_email, type))

# Removes a user from the table. Admin users can only be removed if there's more than one admin remaining
def remove_user(cursor, to_remove):
    if in_table(cursor, to_remove):
        if is_admin(cursor, to_remove): 
            if len(view_admins(cursor)) <= 1:
                return "Error: Must have at least one admin"
        cursor.execute('DELETE FROM perms WHERE email == ?', (to_remove, ))
        return True
    else:
        return "User not found"

# Saves all changes to database
def save(connection):
    connection.commit()