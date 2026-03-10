import sqlite3

#------------------------------
# Viewing all items in database (including items with quantity 0)
#------------------------------

# Returns info for all items in the products table
def view_table(cursor):    
    cursor.execute('SELECT * FROM products')
    return cursor.fetchall()

def view_all_names(cursor):
    """
    Views all item names in products table
    Args:
        cursor (cursor): Allows for connection to the database
    Returns:
        names (list[str]): All of the item names in the database
    """
    cursor.execute('SELECT DISTINCT name FROM products')
    names = [x[0] for x in cursor.fetchall()] 
    names.sort()
    return names 

def view_all_brands(cursor):
    """
    Views all brands in products table
    Args:
        cursor (cursor): Allows for connection to the database
    Returns:
        brands (list[str]): All of the item brands in the database
    """
    cursor.execute('SELECT DISTINCT brand FROM products WHERE NOT brand == ""')
    brands = [x[0] for x in cursor.fetchall()] 
    brands.sort()
    return brands 

# Returns all tags in tags table, whether they're currently connected to an item or not
def view_all_tags(cursor):
    cursor.execute('SELECT * FROM tags')
    return cursor.fetchall()

#------------------------------
# Viewing items currently in the pantry (quantity > 0)
#------------------------------

# Returns the info for all items currently in the pantry (quantity > 0)
def view_pantry_inventory(cursor):
    cursor.execute('SELECT * FROM products WHERE quantity > 0')
    return cursor.fetchall()

# Returns the names of all items currently in the pantry (quantity > 0)
def view_pantry_names(cursor):
    cursor.execute('SELECT DISTINCT name FROM products WHERE quantity > 0')
    names = [x[0] for x in cursor.fetchall()] 
    names.sort()
    return names 

# Returns all of the brands currently in the pantry (quantity > 0)
def view_pantry_brands(cursor):
    cursor.execute('SELECT DISTINCT brand FROM products WHERE NOT brand == "" AND quantity > 0')
    brands = [x[0] for x in cursor.fetchall()] 
    brands.sort()
    return brands 

# Returns all tags currently connected to items in the pantry
def view_pantry_tags(cursor):
    cursor.execute('SELECT id FROM products WHERE quantity > 0')
    ids = [x[0] for x in cursor.fetchall()]
    placeholder_list = ", ".join("?" for t in ids) 
    query = f'SELECT * FROM product_tags WHERE product_id IN ({placeholder_list})'
    cursor.execute(query, ids)
    return cursor.fetchall()

#------------------------------
# Updating methods
#------------------------------

def add_item(cursor, name, brand, id, quantity, image, *tags):
    """
    Adds an item to the table
    Args:
        cursor (cursor): Allows for connection to the database
        name (str): The item's name
        brand (str): The item's brand
        id (int): The barcode id of the item
        quantity (int): The number of items being added
        image (str): The file path to a picture of the item
        tags (str): Tags the item is associated with. An item doesn't have to be added with tags
    Returns:
        cursor: The result of the queries
    """
    cursor.execute('INSERT INTO products VALUES (?, ?, ?, ?, ?)', (name.title(), brand.title(), id, quantity, image))
    for i in tags:
        cursor.execute('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', (i.title(), ))
        cursor.execute('INSERT INTO product_tags VALUES (?, ?)', (id, i.title()))
        
def update_item(cursor, name, brand, id, quantity, image, *tags):
    """
    Updates item info
    Args:
        cursor (cursor): Allows for connection to the database
        name (str): The name of the item
        brand (str): The item's brand
        id (int): The barcode id of the item. Can't be changed
        quantity (int): The number of items being added
        image (str): The path to the image
        tags (str): Tags the item is associated with. An item doesn't have to be added with tags
    Returns:
        cursor: The result of the queries
    """
    if quantity >= 0:
        cursor.execute('SELECT * FROM products WHERE id == ?', (id, )) 
        result = cursor.fetchall()
        if len(result) > 0:
            old_quantity = result[0][3] 
            new_quantity = int(old_quantity) + quantity
            cursor.execute('UPDATE products SET name == ?, brand == ?, quantity == ?, image_link == ? WHERE id == ?', (name.title(), brand.title(), new_quantity, image, id))
            for i in tags:
                cursor.execute('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', (i.title(), ))
                cursor.execute('INSERT INTO product_tags (product_id, tag_label) VALUES (?, ?) ON CONFLICT (product_id, tag_label) DO NOTHING', (id, i.title()))
    else:
        return "Invalid quantity"
    
# Checks out an item from the pantry. Returns error message if quantity is greater than the number of items available
def checkout_item(cursor, id, quantity):
    cursor.execute('SELECT quantity FROM products WHERE id == ?', (id, ))
    old_quantity = cursor.fetchall()[0][0]
    new_quantity = old_quantity - quantity
    if new_quantity >= 0:
        cursor.execute('UPDATE products SET quantity == ?', (new_quantity, ))
    else:
        return "Invalid quantity"

# Adds new tags to the tags table. These tags are not connected to an item yet
def add_tags_to_table(cursor, new_tags):
    for i in new_tags:
        cursor.execute('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', (i.title(), )) 

#------------------------------
# Searching the entire table
#------------------------------

# Returns true if the item is in the table
def in_table(cursor, id):
    if len(search_pantry_by_id(cursor, id)) > 0:
        return True
    return False

# Returns all info for an item, including tags
def get_all_info(cursor, id):
    cursor.execute('SELECT * FROM products WHERE id == ?', (id, ))
    i = cursor.fetchall()
    if len(i) > 0:
        item = list(i[0])
        tags = get_tags_for_item(cursor, id)
        print(tags)
        item.extend(tags)
        return item
    return []

#------------------------------
# Searching pantry (items with quantity > 0)
#------------------------------

# Checks if the name is in the pantry and returns all item info. Returns empty brackets when item isn't found
def search_pantry_by_name(cursor, name):
    cursor.execute('SELECT * FROM products WHERE quantity > 0 AND name == ?', (name.title(), ))
    return cursor.fetchall()

# Checks if the brand is in the pantry and returns all item info. Returns empty brackets when item isn't found
def search_pantry_by_brand(cursor, brand):
    cursor.execute('SELECT * FROM products WHERE quantity > 0 AND brand == ?', (brand.title(), ))
    return cursor.fetchall()

# Checks if the id is in the pantry and returns all item info. Returns empty brackets when item isn't found
def search_pantry_by_id(cursor, id):
    cursor.execute('SELECT * FROM products WHERE quantity > 0 AND id == ?', (id, ))
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
    cursor.execute('SELECT product_id FROM product_tags WHERE tag_label == ?', (tag.title(), ))
    ids = [x[0] for x in cursor.fetchall()]
    placeholder_list = ", ".join("?" for t in ids)
    query = f'SELECT * FROM products WHERE quantity > 0 AND id IN ({placeholder_list})'
    cursor.execute(query, ids) 
    return cursor.fetchall()

#------------------------------
# Getting item info
#------------------------------

# Returns all of the tags associated with an item
def get_tags_for_item(cursor, id):
    cursor.execute('SELECT * FROM product_tags WHERE product_id == ?', (id, ))
    tags = [x[1] for x in cursor.fetchall()]
    return tags

# Gets the filepath of an image. Returns [] if image is not in table
def view_image(cursor, id):
    cursor.execute('SELECT image_link FROM products WHERE id == ?', (id, ))
    path = cursor.fetchall()
    if len(path) > 0:
        path = path[0][0]
    return path

#------------------------------
# Removing methods
#------------------------------

# Completely removes an item and associated tags from the table
def delete_item(cursor, id):
    cursor.execute('DELETE FROM products WHERE id == ?', (id, ))
    cursor.execute('DELETE FROM product_tags WHERE product_id == ?', (id, ))

# Completely removes a tag from the table
def delete_tag(cursor, tag):
    cursor.execute('DELETE FROM product_tags WHERE tag_label == ?', (tag, ))
    cursor.execute('DELETE FROM tags WHERE label == ?', (tag, ))

#------------------------------
# Saving methods
#------------------------------

# Saves the changes to the database
def save(connection):
    connection.commit()

#------------------------------
# Needs fixing
#------------------------------

# Set image.
# TODO: This still needs a way to get the actual image info from the user
def set_image(cursor, id):
    image_path = f'/workspaces/Pirate-Pantry-Inventory-Tracking/images/{id}.jpg'
    cursor.execute('UPDATE products SET image_link == ? WHERE id == ?', (image_path, id))