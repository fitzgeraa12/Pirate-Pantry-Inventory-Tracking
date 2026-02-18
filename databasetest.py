import sqlite3 #Allows for interaction with the database
import random #To generate a random id


"""Returns a list of all items sorted by name"""
def pull_names(cursor):
    cursor.execute('SELECT DISTINCT name FROM Test_table') #Gets all unique item names 
    all_names = [x[0] for x in cursor.fetchall()] #sql saves results as a tuple, so gets the first element of the tuple
    return all_names
    
"""Gets a list of all groups currently in the database"""
def pull_groups(cursor):
    cursor.execute('SELECT DISTINCT food_group FROM Test_table')
    all_groups = [x[0] for x in cursor.fetchall()]
    print(all_groups)
    return all_groups

"""Allows a user to pull all items from the same food group"""
def group_search(cursor):
    all_groups = pull_groups(cursor)
    print("Choose a group:")
    answer = input()
    print(f"All {answer} in the database:")
    cursor.execute(f'SELECT name FROM Test_table WHERE food_group = "{answer}"')
    specific_groups = [x[0] for x in cursor.fetchall()][0]
    print(specific_groups)

"""Prints all of the data in the table"""
def view(cursor):
    print("Updated table:")
    cursor.execute('SELECT * FROM Test_table') #SQL command to select all data from the table - .execute runs the specific command
    print(cursor.fetchall()) #fetchall fetches everything the sql query returns

def update_table(cursor, quantity, id):
    cursor.execute(f'SELECT quantity FROM Test_table WHERE id = "{id}"')
    og_quantity = cursor.fetchall()[0][0]
    new_quantity = int(og_quantity) + int(quantity)    
    cursor.execute(f'UPDATE Test_table SET quantity = "{new_quantity}" WHERE id = "{id}"')

"""Adds to an item that already exists in the table"""
def add_by_id(cursor, id):
    cursor.execute(f'SELECT * FROM Test_table WHERE id = "{id}"') #Searches for item by id
    get_item = cursor.fetchall()
    print(f'Adding to "{3}" items to: "{get_item}"') #Double check to make sure the user knows what items they're adding and to what
    update_table(cursor, 3, id)
    cursor.execute(f'SELECT * FROM Test_table WHERE id = "{id}"') #Searches the item to get the updated value
    get_item = cursor.fetchall()
    print(f'Updated value: {get_item}')

"""Adding an item to the database. id is randomly generated for now"""
def add_new(name, brand, group, quantity, cursor):
    cursor.execute(f'INSERT INTO Test_table VALUES ("{name}", "{brand}", "{random.randint(0, 1000)}", "{group}", "{quantity}", "None")') #Query for adding a record to the database

def main():
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_table.db') #Connects to existing database
    cursor = connection.cursor() #The cursor is what lets you traverse over the database- what allows you to query records!
    add_new('Nacho Cheese Doritos','Doritos','carbs',6, cursor) #Manually adds bag of doritos to table
    add_by_id(cursor, 1222) #Adds 3 more cups of kraft mac n cheese
    view(cursor)
    pull_names(cursor)
    group_search(cursor)
    cursor.close() #Closes connection and cursor
    connection.close()

#Have tags to separate items- carbs, chips, gluten free, gluten free
#Could have a field that's just 'tags' that holds a string of all possible tags (carbs, chips, peanut-free...) but I feel like you'd have to do a search in the string everytime you'd want a specific tag
#Have a tags table that is sorted by id (not food name bc the id stores the brand- will have allergy information)
#tags table has id and wtv tags the want. i think each tag would be a field and it's a boolean value? 
#id: 1234, chips: 1, carbs: 1, peanut free: 1, gluten free: 0, vegtables: 0

if __name__ == "__main__":
    main()