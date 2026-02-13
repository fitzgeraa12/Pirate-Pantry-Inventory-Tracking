import sqlite3 #Allows for interaction with the database
import random #To generate a random id

connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test2.db') #Connects to existing database

cursor = connection.cursor() #The cursor is what lets you traverse over the database- what allows you to query records!

get_table = 'SELECT * FROM test2' #SQL command to select all data from the table
print("TABLE VIEW: name, brand, ID, group, quantity, image")
cursor.execute(get_table) #.execute runs the specific command
print(cursor.fetchall()) #fetchall fetches everything the sql query returns

print("----------------- ADD ITEM SIMULATION -----------------") #Simulation for adding an item to the table. Image and scanner don't work here
print("(pov: you're a whitelisted user who wants to add an item)")
print("(everything is done using manual entry & typing)")
print("-->Insert name: ")
name = input()
print("-->Insert brand: ")
brand = input()
print("-->Insert food group")
group = input()
print(f"-->How many {name}s are you adding?")
quantity = input()
print("-->pretend an image was added")
print(name, brand, group, quantity)

adding = f'INSERT INTO test2 VALUES ("{name}", "{brand}", "{random.randint(0, 1000)}", "{group}", "{quantity}", "None")' #Query for adding a record to the database
cursor.execute(adding) #Executes query to add the item
cursor.execute(get_table) #Executes query to get all data from the table
print(cursor.fetchall()) #Prints all data in table

print("Save changes? (y/n)") #User can choose to save data to the table
answer = input()
if answer == "y":
    connection.commit() #Saves all changes to test database
cursor.close() #Closes connection and cursor
connection.close()