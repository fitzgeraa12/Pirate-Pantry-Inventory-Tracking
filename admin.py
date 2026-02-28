import sqlite3

#Returns all users in the table
def view_all(cursor):
    cursor.execute('SELECT * FROM security_info')
    return cursor.fetchall()

#Returns all admin users in the table
def view_admins(cursor):
    cursor.execute('SELECT * FROM security_info WHERE type == \'admin\'')
    return cursor.fetchall()

#Returns all trusted users in the table
def view_trusted(cursor):
    cursor.execute('SELECT * FROM security_info WHERE type == \'trusted\'')
    return cursor.fetchall()

#Returns true if the email is a trusted or admin user
def in_table(cursor, email):
    cursor.execute('SELECT * FROM security_info WHERE email == ?', (email, ))
    if len(cursor.fetchall()) > 0:
        return True
    return False

#Returns true if the user is an admin, false if they're trusted
def is_admin(cursor, email):
    cursor.execute('SELECT * FROM security_info WHERE email == ? AND type == \'admin\'', (email, ))
    if len(cursor.fetchall()) > 0:
        return True
    return False

#TODO: should the database be checking if the user is an admin, or should the API? Also should the API check type is either admin or trusted?
#Adds a new user to the table
def add_user(cursor, new_email, type, user_email):
    if is_admin(cursor, user_email):
        cursor.execute('INSERT INTO security_info VALUES (?, ?)', (new_email, type))
        return True
    return False

#Removes a user from the table. Admin users can only be removed if there's more than one admin remaining
#TODO: Should we get special permissions? Also can a user remove themself?
def remove_user(cursor, to_remove):
    if in_table(cursor, to_remove):
        if is_admin(cursor, to_remove): 
            if len(view_admins(cursor)) <= 1:
                return "Error: Must have at least one admin"
        cursor.execute('DELETE FROM security_info WHERE email == ?', (to_remove, ))
        return True
    else:
        return "User not found"

#Saves all changes to database
def save(connection):
    connection.commit()
