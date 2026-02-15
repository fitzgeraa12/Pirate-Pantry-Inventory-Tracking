import sqlite3 #Allows for interaction with the database
import random #To generate a random id


"""Adding an item to the database. id is randomly generated for now"""
def add(name, brand, group, quantity, cursor):
    add_query = f'INSERT INTO Test_table VALUES ("{name}", "{brand}", "{random.randint(0, 1000)}", "{group}", "{quantity}", "None")' #Query for adding a record to the database
    cursor.execute(add_query) #Executes query to add the item


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
    cursor.execute(f'SELECT * FROM Test_table WHERE food_group = "{answer}"')
    specific_groups = cursor.fetchall()
    print(specific_groups)

"""Prints all of the data in the table"""
def view(cursor):
    get_table = 'SELECT * FROM Test_table' #SQL command to select all data from the table
    cursor.execute(get_table) #.execute runs the specific command
    print(cursor.fetchall()) #fetchall fetches everything the sql query returns

def main():
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_table.db') #Connects to existing database
    cursor = connection.cursor() #The cursor is what lets you traverse over the database- what allows you to query records!
    #add('test','Test_table','test3',6, cursor)
    view(cursor)
    #pull_names(cursor)
    group_search(cursor)
    #print("Save changes? (y/n)") #User can choose to save data to the table
    #answer = input()
    #if answer == "y":
    #    connection.commit() #Saves all changes to test database
    cursor.close() #Closes connection and cursor
    connection.close()

if __name__ == "__main__":
    main()