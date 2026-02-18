import sqlite3 #Allows for interaction with the database
import random #To generate a random id

"""Returns a list of all items sorted by name"""
def pull_names(cursor):
    cursor.execute('SELECT DISTINCT name FROM Test_table') #Gets all unique item names 
    all_names = [x[0] for x in cursor.fetchall()] #sql saves results as a tuple, so gets the first element of the tuple
    return all_names
    
"""Gets a list of all groups currently in the database
    (We're no longer sorting items by groups, but this is good for testing purposes)"""
def pull_groups(cursor):
    cursor.execute('SELECT DISTINCT food_group FROM Test_table')
    all_groups = [x[0] for x in cursor.fetchall()]
    print(all_groups)
    return all_groups

"""Allows a user to look at all items from the same food group"""
def group_search(cursor, group_name):
    all_groups = pull_groups(cursor)
    cursor.execute(f'SELECT name FROM Test_table WHERE food_group = "{group_name}"')
    specific_groups = [x[0] for x in cursor.fetchall()][0]
    print(specific_groups) #print statement is for debug
    return specific_groups

"""Prints all of the data in the table"""
def view(cursor):
    print("Updated table:")
    cursor.execute('SELECT * FROM Test_table') #SQL command to select all data from the table - .execute runs the specific command
    all_data = cursor.fetchall()
    print(all_data) #fetchall fetches everything the sql query returns

"""Helper method that updates the quantity of an item"""
def update_table(cursor, quantity, id):
    cursor.execute(f'SELECT quantity FROM Test_table WHERE id = "{id}"')
    og_quantity = cursor.fetchall()[0][0]
    new_quantity = int(og_quantity) + int(quantity)    
    cursor.execute(f'UPDATE Test_table SET quantity = "{new_quantity}" WHERE id = "{id}"')

"""Adds to an item that already exists in the table"""
def update_quantity(cursor, id, quantity):
    cursor.execute(f'SELECT * FROM Test_table WHERE id = "{id}"') #Searches for item by id (need a case for if id doesn't exist)
    get_item = cursor.fetchall()
    update_table(cursor, quantity, id)
    cursor.execute(f'SELECT * FROM Test_table WHERE id = "{id}"') #Searches the item to get the updated value
    get_item = cursor.fetchall()
    print(f'Updated value: {get_item}')
    return get_item

"""Adding a brand new item to the database"""
def add_new(name, brand, id, group, quantity, cursor):
    cursor.execute(f'INSERT INTO Test_table VALUES ("{name}", "{brand}", "{id}", "{group}", "{quantity}", "None")') #Query for adding a record to the database

def main():
    #These four lines should be pasted anytime you want to use the database. Make sure the cursor is passed in to each method
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_table.db') #Connects to existing database
    cursor = connection.cursor() #The cursor is what lets you traverse over the database- what allows you to query records!
    cursor.close() #Closes connection and cursor
    connection.close()

if __name__ == "__main__":
    main()