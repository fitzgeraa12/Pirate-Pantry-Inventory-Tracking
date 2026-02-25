import sqlite3

# Returns info for all items in the main table
def view_table(cursor):    
    cursor.execute('SELECT * FROM main_table')
    return cursor.fetchall()

# Returns the info for all items with a quantity > 0
def view_inventory(cursor):
    cursor.execute('SELECT * FROM main_table WHERE NOT quantity == \'0\'')
    return cursor.fetchall()

# Returns all tags in tag_table, whether they're currently connected to an item or not
def view_all_tags(cursor):
    cursor.execute('SELECT * FROM tag_table')
    return cursor.fetchall()

# Returns all tags that are currently associated with an item
def view_item_tags(cursor):
    cursor.execute('SELECT id FROM main_table WHERE NOT quantity == \'0\'') #All of the items actually present in the pantry
    ids = [x[0] for x in cursor.fetchall()] #Saves all items to a list
    ids_list = ", ".join(str(t) for t in ids) #Formatting list so SQL can read it
    cursor.execute(f'SELECT * FROM junction_table WHERE id IN ({ids_list})') #junction_table is the table that connects items to tags. 
    return cursor.fetchall()

def view_all_names(cursor):
    """
    Views all item names in main table
    Args:
        cursor (cursor): Allows for connection to the database
    Returns:
        names (list[str]): All of the item names in the database
    """
    cursor.execute('SELECT DISTINCT name FROM main_table') #Only unique elements are stored
    names = [x[0] for x in cursor.fetchall()] 
    names.sort() #Alphabetizes items
    return names 

def view_all_brands(cursor):
    """
    Views all brands in main table
    Args:
        cursor (cursor): Allows for connection to the database
    Returns:
        brands (list[str]): All of the item names in the database
    """
    cursor.execute('SELECT DISTINCT brand FROM main_table WHERE NOT brand == "''"') #Only unique elements are stored and brands with a null field aren't saved
    brands = [x[0] for x in cursor.fetchall()] 
    brands.sort() #Alphabetizes items
    return brands 

def add_tags(cursor, new_tags):
    """
    Adds new tags to the tag_table
    Args:
        cursor (cursor): Allows for connection to the database
        new_tags (list[str]): A list of tags to add
    Returns:
        cursor: The result of the queries
    """
    for i in new_tags:
        cursor.execute(f'INSERT INTO tag_table VALUES ("{i.title()}")')
    print(view_all_tags(cursor))

def add_new_item(cursor, name, brand, id, quantity, image, tags):
    """
    Adds a brand new item to the table. No new tags were created
    Args:
        cursor (cursor): Allows for connection to the database
        name (str): The item's name
        brand (str): The item's brand
        id (int): The barcode id of the item
        quantity (int): The number of items being added
        image (str): Right now is the string 'None'. A picture of the item
        tags (list[str]): A list of tags the item is associated with
    Returns:
        cursor: The result of the queries
    """
    cursor.execute(f'INSERT INTO main_table VALUES ("{name.title()}", "{brand.title()}", "{id}", "{quantity}", "{image}")') #.title() converts spelling to title case
    for i in tags: #Connects all tags to their item in title table
        cursor.execute(f'INSERT INTO junction_table VALUES ("{id}", "{i.title()}")')
    cursor.execute('SELECT * FROM junction_table')
    return cursor.fetchall()

def update_item(cursor, id, quantity):
    """
    Updates the quantity of an item in the table. Makes no other changes
    Args:
        cursor (cursor): Allows for connection to the database
        id (int): The barcode id of the item
        quantity (int): The number of items being added
    Returns:
        cursor: The result of the queries
    """
    cursor.execute(f'SELECT quantity FROM main_table WHERE id == {id}')
    old_quantity = cursor.fetchall()[0][0]
    new_quantity = int(old_quantity) + quantity
    cursor.execute(f'UPDATE main_table SET quantity =={new_quantity} WHERE id == {id}')
    print(view_table(cursor))

def get_item_by_tag(cursor, tag):
    """
    Returns all the items associated with desired tag
    Args:
        cursor (cursor): Allows for connection to the database
        tag (str): The tag of an item
    Returns:
        cursor: The result of the queries
    """
    cursor.execute(f'SELECT id FROM junction_table WHERE tag == \'{tag.title()}\'') #Gets the id from junction_table
    id = [x[0] for x in cursor.fetchall()]
    id_list = ", ".join(str(t) for t in id) #Saves id information so SQL can read it
    cursor.execute(f'SELECT * FROM main_table WHERE id IN ({id_list})') 
    return cursor.fetchall()

#Checks if the id is in the database and returns all item info. Returns empty brackets when item isn't found
def search_by_id(cursor, id):
    cursor.execute(f'SELECT * FROM main_table WHERE id == \'{id}\'')
    return cursor.fetchall()

#Checks if the name is in the database and returns all item info. Returns empty brackets when item isn't found
def search_by_name(cursor, name):
    cursor.execute(f'SELECT * FROM main_table WHERE name == \'{name.title()}\'')
    return cursor.fetchall()

#Checks if the brand is in the database and returns all item info. Returns empty brackets when item isn't found
def search_by_brand(cursor, brand):
    cursor.execute(f'SELECT * FROM main_table WHERE brand == \'{brand.title()}\'')
    return cursor.fetchall()

#Checks if the tag is in the database and returns the id. Returns empty brackets when an item isn't found
def search_by_tag(cursor, tag):
    cursor.execute(f'SELECT * FROM junction_table WHERE tag == \'{tag.title()}\'')
    #TODO: Ask if the id or all item info should be returned
    return cursor.fetchall()

#Saves the changes to the database
def save(connection):
    connection.commit()

#TODO: image?
#TODO: create db with user permission status

def main():
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db')
    cursor = connection.cursor()
    #print(view_table(cursor))
    #print(view_inventory(cursor))
    #print(view_item_tags(cursor))
    print(view_all_tags(cursor))
    #print(add_new_item(cursor, 'Peanut Butter', 'HEB', 2222, 9, 'None', ['Carbs'])) #Capitlization is weird to replicate user error
    #print(view_table(cursor))
    #update_item(cursor, 1234, 5)
    #print(get_item_by_tag(cursor, 'carbs'))
    #add_tags(cursor, ['Contains dairy', 'Chips', 'Candy', 'pasta'])
    #print(view_all_names(cursor))
    #print(view_all_brands(cursor))
    #print(search_by_id(cursor, 1234))
    #print(search_by_name(cursor, 'Peanut Butter'))
    #print(search_by_brand(cursor, 'Jiffy'))
    #print(search_by_tag(cursor, 'carbs'))
    #save(connection)
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()