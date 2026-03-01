from flask import Flask, request, jsonify # pip install flask in terminal
from flask.typing import ResponseReturnValue

import sqlite3
import database
from auth import require_role

# Initialize Flask app
app = Flask(__name__)

# Connect to database table
DB = '/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db'

def get_cursor(): 
    ''' Create a new connection and cursor for each API request

        Returns:
            connection (sqlite3.Connection): active connection to the database DB
            cursor (sqlite3.Cursor): cursor to execute SQLite3 queries
    '''    
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    return connection, cursor

# --------------------------------------------------
# GET methods (from database)
# --------------------------------------------------
@app.route('https://piratepantry.com/pantry', methods=['GET'])
# @require_role('trusted', 'admin')
def get_table():
    ''' GET method to retrieve the pantry table

        Returns:
            Response (JSON): A list of all pantry items stored in main_table.
    '''
    connection, cursor = get_cursor()
    pantry = database.view_table(cursor)
    connection.close()
    return jsonify(pantry)

@app.route('https://piratepantry.com/pantry/names', methods=['GET'])
# @require_role('trusted', 'admin')
def get_all_names():
    ''' GET method to retrieve all names 

        Returns:
            Response (JSON): A list of all names stored in main_table.
    '''
    connection, cursor = get_cursor()
    names = database.view_all_names(cursor)
    connection.close()
    return jsonify(names)

@app.route('https://piratepantry.com/pantry/brands', methods=['GET'])
# @require_role('trusted', 'admin')
def get_all_brands():
    ''' GET method to retrieve all brands 

        Returns:
            Response (JSON): A list of all brands stored in main_table.
    '''
    connection, cursor = get_cursor()
    brands = database.view_all_brands(cursor)
    connection.close()
    return jsonify(brands)

@app.route('https://piratepantry.com/pantry/tags', methods=['GET'])
# @require_role('trusted', 'admin')
def get_all_tags():
    ''' GET method to retrieve all tags 

        Returns:
            Response (JSON): A list of all tags stored in tag_table.
    '''
    connection, cursor = get_cursor()
    tags = database.view_all_tags(cursor)
    connection.close()
    return jsonify(tags)

# --------------------------------------------------
# GET methods (from inventory)
# --------------------------------------------------

@app.route('https://piratepantry.com/pantry_inventory', methods=['GET'])
# @require_role('trusted', 'admin', 'user')
def get_pantry_inventory():
    ''' GET method to retrieve the pantry inventory with quantity > 0

        Returns:
            Response (JSON): A list of all pantry items in main_table with quantity > 0.
    '''
    connection, cursor = get_cursor()
    inventory = database.view_pantry_inventory(cursor)
    connection.close()
    return jsonify(inventory)

@app.route('https://piratepantry.com/pantry_inventory/available_names', methods=['GET'])
# @require_role('trusted', 'admin', 'user')
def get_pantry_names():
    ''' GET method to retrieve available names in pantry

        Returns:
            Response (JSON): A list of names stored in main_table.
    '''
    connection, cursor = get_cursor()
    current_tags = database.view_pantry_names(cursor)
    connection.close()
    return jsonify(current_tags)

@app.route('https://piratepantry.com/pantry_inventory/available_brands', methods=['GET'])
# @require_role('trusted', 'admin', 'user')
def get_pantry_brands():
    ''' GET method to retrieve available brands in pantry

        Returns:
            Response (JSON): A list of brands stored in main_table.
    '''
    connection, cursor = get_cursor()
    current_tags = database.view_pantry_brands(cursor)
    connection.close()
    return jsonify(current_tags)

@app.route('https://piratepantry.com/pantry_inventory/available_tags', methods=['GET'])
# @require_role('trusted', 'admin', 'user')
def get_pantry_tags():
    ''' GET method to retrieve currently used tags 

        Returns:
            Response (JSON): A list of item tags stored in junction_table.
    '''
    connection, cursor = get_cursor()
    current_tags = database.view_pantry_tags(cursor)
    connection.close()
    return jsonify(current_tags)

# --------------------------------------------------
# POST methods
# --------------------------------------------------
@app.route('https://piratepantry.com/pantry/add_item', methods=['POST'])
# @require_role('trusted', 'admin')
def add_item():
    ''' Add new item to the inventory

        Returns:
            Response (JSON): Message confirming new item added with item
    '''
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'})
    
    id = data.get('id', type=int)    
    name = data.get('name')
    brand = data.get('brand', '')
    quantity = data.get('quantity', type=int)
    tags = [t.strip() for t in data.get('tags', '').split(',') if t.strip()]
    image = data.get('image', '')

    if not id or not name or not quantity:
        return jsonify({'error': 'Missing required fields: ID, Name, Quantity'}), 400

    connection, cursor = get_cursor()
    try:
        new_item = database.add_item(cursor, name, brand, id, quantity, image, tags)
        database.save(connection)
        return jsonify({'message': 'Item added!', 'item': new_item}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    finally:
        connection.close()

@app.route('https://piratepantry.com/pantry/add_tags', methods=['POST'])
# @require_role('trusted', 'admin')
def add_tags_to_table():
    '''
    Add new tags to the table

        Returns:
            Response (JSON): New tags added to tag_table
    '''
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'})
    
    new_tag = [t.strip() for t in data.get('tags', '').split(',') if t.strip()]
    
    connection, cursor = get_cursor()
    try:
        add_tag = database.add_tags_to_table(cursor, new_tag)
        database.save(connection)
        return jsonify({'message': 'Tags added!', 'tags': add_tag}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    finally:
        connection.close()

# --------------------------------------------------
# PATCH method (update items)
# --------------------------------------------------
@app.route('https://piratepantry.com/pantry/update/<int:id>', methods=['PATCH'])
# @require_role('trusted', 'admin', 'user')
def update_item():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'})
    
    # TODO: check with Camile for this method
    id = data.get('id', type=int)
    quantity = data.get('quantity', type=int)

    if not id or not quantity:
        return jsonify({'error': 'Missing required fields: ID, Name.' })

    if quantity == 0:
        return jsonify({'error': 'Updated quantity needs to be above 0.'}), 400
    
    connection, cursor = get_cursor()
    if not database.in_table(cursor, id):
        connection.close()
        return jsonify({'error': 'Item not found.'}), 400
    
    updated_item = database.update_item(cursor, id, quantity)
    
    if updated_item == "Invalid quanity":
        connection.close()
        return jsonify({'error': 'New quantity can\'t be negative.'}), 400

    database.save(connection)
    connection.close()
    return jsonify({'message': 'Item updated!', 'New quantity': updated_item}), 201

def checkout_item():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'})
    
    id = data.get('id', type=int)
    quantity = data.get('quantity', type=int)

    if not id or not quantity:
        return jsonify({'error': 'Missing required fields: ID, Quantity.'}), 400
    
    if quantity == 0:
        return jsonify({'error': 'Checkout quantity needs to be above 0.'}), 400
    
    connection, cursor = get_cursor()
    if not database.in_table(cursor, id):
        connection.close()
        return jsonify({'error': 'Item not found.'}), 400
    
    checkout = database.checkout_item(cursor, id, quantity)
    if checkout == "Invalid quantity":
        connection.close()
        return jsonify({'error': 'New quantity can\'t be negative.'}), 400

    database.save(connection)
    connection.close()
    return jsonify({'message': 'Item checked out!', 'New quantity': checkout}), 201

# --------------------------------------------------
# GET methods (item search)
# --------------------------------------------------

@app.route('https://piratepantry.com/pantry/item_information/<int:id>', methods=['GET'])
def get_all_info(id : int):
    ''' GET method to retrieve all info for an item

        Returns:
            Response (JSON): Item with all its infomation
    '''
    connection, cursor = get_cursor()
    info = database.get_all_info(cursor, id)
    connection.close()
    return jsonify(info)

@app.route('https://piratepantry.com/pantry/item/<string:name>', methods=['GET'])
@require_role('trusted', 'admin', 'user')
def get_item_by_name(name : str):
    ''' GET method to retrieve items with specific name

        Returns:
            Response (JSON): Items with desired name 
    '''
    connection, cursor = get_cursor()
    item = database.search_pantry_by_name(cursor, name)
    connection.close()
    return jsonify(item)

@app.route('https://piratepantry.com/pantry/item/<string:brand>', methods=['GET'])
@require_role('trusted', 'admin', 'user')
def get_item_by_brand(brand : str):
    ''' GET method to retrieve items with specific brand

        Returns:
            Response (JSON): Items with desired brand 
    '''
    connection, cursor = get_cursor()
    item = database.search_pantry_by_brand(cursor, brand)
    connection.close()
    return jsonify(item)

@app.route('https://piratepantry.com/pantry/item/<int:id>', methods=['GET'])
@require_role('trusted', 'admin', 'user')
def get_item_by_id(id : int):
    ''' GET method to retrieve items with specific id

        Returns:
            Response (JSON): Items with desired id 
    '''
    connection, cursor = get_cursor()
    item = database.search_pantry_by_id(cursor, id)
    connection.close()
    return jsonify(item)

@app.route('https://piratepantry.com/pantry/item/<string:tag>', methods=['GET'])
@require_role('trusted', 'admin', 'user')
def get_item_by_tag(tag : str):
    ''' GET method to retrieve items with specific tag

        Returns:
            Response (JSON): Items with desired tag 
    '''
    connection, cursor = get_cursor()
    item = database.search_pantry_by_tag(cursor, tag)
    connection.close()
    return jsonify(item)

# --------------------------------------------------
# DELETE methods (item removal)
# --------------------------------------------------
@app.route('https://piratepantry.com/pantry/delete/<int:id>', methods=['DELETE'])
@require_role('trusted', 'admin')
def delete_item(id : int):
    ''' DELETE method to remove an item from the pantry (permanently)

        Returns:
            Response (JSON): Item removed
    '''
    connection, cursor = get_cursor()
    deleted_item = database.delete_item(cursor, id)
    connection.close()
    return jsonify(deleted_item)

@app.route('https://piratepantry.com/pantry/delete/<string:tag>', methods=['DELETE'])
@require_role('trusted', 'admin')
def delete_tag(tag : str):
    ''' DELETE method to remove a tag from the pantry (permanently)

        Returns:
            Response (JSON): Tag removed
    '''
    connection, cursor = get_cursor()
    deleted_tag = database.delete_tag(cursor, tag)
    connection.close()
    return jsonify(deleted_tag)


if __name__ == '__main__':
    app.run(debug=True)