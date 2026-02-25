import sqlite3

#------------------------------
# Viewing all items in database (including items with quantity 0)
#------------------------------

# Returns info for all items in the main table
def view_table(cursor):    
    cursor.execute('SELECT * FROM main_table')
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

# Returns all tags in tag_table, whether they're currently connected to an item or not
def view_all_tags(cursor):
    cursor.execute('SELECT * FROM tag_table')
    return cursor.fetchall()

#Gets the filepath of an image. Returns [] if image is not in table
def view_image(cursor, id):
    param = (id,)
    cursor.execute('SELECT image FROM main_table WHERE id == ?', param)
    path = cursor.fetchall()
    if len(path) > 0:
        path = path[0][0]
    return path

#------------------------------
# Viewing items currently in the pantry (quantity > 0)
#------------------------------

# Returns the info for all items currently in the pantry (quantity > 0)
def view__pantry_inventory(cursor):
    cursor.execute('SELECT * FROM main_table WHERE quantity > 0')
    return cursor.fetchall()

def view_pantry_names(cursor):
    cursor.execute('SELECT DISTINCT name FROM main_table WHERE quantity > 0') #Only unique elements are stored
    names = [x[0] for x in cursor.fetchall()] 
    names.sort() #Alphabetizes items
    return names 

def view_pantry_brands(cursor):
    cursor.execute('SELECT DISTINCT brand FROM main_table WHERE NOT brand == "''" AND quantity > 0') #Only unique elements are stored and brands with a null field aren't saved
    brands = [x[0] for x in cursor.fetchall()] 
    brands.sort() #Alphabetizes items
    return brands 

# Returns all tags that are currently associated with an item
def view_pantry_tags(cursor):
    cursor.execute('SELECT id FROM main_table WHERE quantity > 0') #All of the items actually present in the pantry
    ids = [x[0] for x in cursor.fetchall()] #Saves all items to a list
    placeholder_list = ", ".join("?" for t in ids) 
    query = f'SELECT * FROM junction_table WHERE id IN ({placeholder_list})' #junction_table is the table that connects items to tags. 
    cursor.execute(query, ids)
    return cursor.fetchall()

#------------------------------
# ADDING METHODS
#------------------------------

#TODO: extra** more
def add_item(cursor, name, brand, id, quantity, image, tags):
    """
    Adds a brand new item to the table. No new tags were created
    Args:
        cursor (cursor): Allows for connection to the database
        name (str): The item's name
        brand (str): The item's brand
        id (int): The barcode id of the item
        quantity (int): The number of items being added
        image (str): The file path to a picture of the item
        tags (list[str]): A list of tags the item is associated with
    Returns:
        cursor: The result of the queries
    """
    if search_table_by_id(cursor, id): #If the item is already saved in the table, update item instead of trying to add a new one
        update_item(cursor, id, quantity)
    else:
        cursor.execute('INSERT INTO main_table VALUES (?, ?, ?, ?, ?)', (name.title(), brand.title(), id, quantity, image)) #.title() converts spelling to title case
        for i in tags: #Connects all tags to their item in title table
            cursor.execute('INSERT INTO junction_table VALUES (?, ?)', (id, i.title()))
        cursor.execute('SELECT * FROM junction_table')
        

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
    cursor.execute('SELECT quantity FROM main_table WHERE id == ?', (id, )) 
    result = cursor.fetchall()
    if len(result) > 0: #If the id is in the database
        old_quantity = result[0][0]
        new_quantity = int(old_quantity) + quantity
        if new_quantity >= 0:
            cursor.execute('UPDATE main_table SET quantity == ? WHERE id == ?', (new_quantity, id))

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
        cursor.execute('INSERT INTO tag_table VALUES (?)', (i.title(), ))


#------------------------------
# Searching the entire table
#------------------------------

#Searches table by id
def search_table_by_id(cursor, id):
    cursor.execute('SELECT * FROM main_table WHERE id == ?', (id, ))
    return cursor.fetchall()

#------------------------------
# Searching pantry (items with quantity > 0)
#TODO: These methods should also return tag info
#------------------------------
#TODO: I think searching the pantry and table should be separate methods- there are times when an admin would only want to see items currently in the pantry
# I can add another check in my search_table_by_x to see if the user is admin?
#Checks if the name is in the pantry and returns all item info. Returns empty brackets when item isn't found
def search_pantry_by_name(cursor, name):
    cursor.execute('SELECT * FROM main_table WHERE quantity > 0 AND name == ?', (name.title(), ))
    return cursor.fetchall()

#Checks if the brand is in the pantry and returns all item info. Returns empty brackets when item isn't found
def search_pantry_by_brand(cursor, brand):
    cursor.execute('SELECT * FROM main_table WHERE quantity > 0 AND brand == ?', (brand.title(), ))
    return cursor.fetchall()

#Checks if the id is in the pantry and returns all item info. Returns empty brackets when item isn't found
def search_pantry_by_id(cursor, id):
    cursor.execute('SELECT * FROM main_table WHERE quantity > 0 AND id == ?', (id, ))
    return cursor.fetchall()

def search_pantry_by_tag(cursor, tag):
    """
    Returns all the items associated with desired tag
    Args:
        cursor (cursor): Allows for connection to the database
        tag (str): The tag of an item
    Returns:
        cursor: The result of the queries
    """
    cursor.execute('SELECT id FROM junction_table WHERE tag == ?', (tag.title(), )) #Gets the id from junction_table
    id = [x[0] for x in cursor.fetchall()]
    placeholder_list = ", ".join("?" for t in id)
    query = f'SELECT * FROM main_table WHERE quantity > 0 AND id IN ({placeholder_list})'
    cursor.execute(query, id) 
    return cursor.fetchall()

#------------------------------
# SAVING METHODS
#------------------------------

#Saves the changes to the database
def save(connection):
    connection.commit()

#------------------------------
# NEEDS FIXING
#------------------------------

#Set image. 
# TODO: This still needs a way to get the actual image info from the user
def set_image(cursor, id):
    image_path = f'/workspaces/Pirate-Pantry-Inventory-Tracking/images/{id}.jpg'
    cursor.execute('UPDATE main_table SET image == ? WHERE id == ?', (image_path, id)) 


def main():
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db')
    cursor = connection.cursor()
    #print(view_table(cursor))
    #print(view_all_names(cursor))
    #print(view_all_brands(cursor))
    #print(view_pantry_names(cursor))
    #print(view_pantry_brands(cursor))
    print(view_pantry_tags(cursor))

    #print(view_inventory(cursor))
    #print(view_all_tags(cursor))
    #print(view_all_tags(cursor))
    #add_item(cursor, 'peanuT butter', 'HEB', 555, 9, 'None', ['Carbs']) #Capitlization is weird to replicate user error. I also think types should be checked before getting to database
    #print(view_table(cursor))
    #update_item(cursor, 1234, 5)
    #print(view_table(cursor))
    #print(get_item_by_tag(cursor, 'carbs'))
    #add_tags(cursor, ['Contains dairy', 'Chips', 'Candy', 'pasta'])
    #print(view_pantry_names(cursor))
    #print(search_pantry_by_id(cursor, 1234))
    #print(search_pantry_by_name(cursor, 'potato soup'))
    #print(search_pantry_by_brand(cursor, 'green giant'))
    #print(search_pantry_by_tag(cursor, 'carbs'))
    #set_image(cursor, 5555)
    #print(view_image(cursor, 5555))
    #save(connection)
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()