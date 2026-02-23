from flask import Flask, request, jsonify # pip install flask in terminal
from flask.typing import ResponseReturnValue

import sqlite3
import database

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
    connection = sql.connect(DB)
    cursor = connection.cursor()
    return connection, cursor

# --------------------------------------------------
# GET methods
# --------------------------------------------------
@app.route('/pantry', methods=['GET'])
def get_pantry():
    ''' GET method to retrieve the pantry table

        Returns:
            Response (JSON): A list of all pantry items stored in main_table.
    '''
    connection, cursor = get_cursor()
    pantry = database.view_table(cursor)
    connection.close()
    return jsonify(pantry)

@app.route('/pantry/current_inventory', methods=['GET'])
def get_inventory():
    ''' GET method to retrieve the pantry inventory with quantity > 0

        Returns:
            Response (JSON): A list of all pantry items in main_table with quantity > 0.
    '''
    connection, cursor = get_cursor()
    inventory = database.view_inventory(cursor)
    connection.close()
    return jsonify(inventory)

@app.route('/pantry/tags', methods=['GET'])
def get_all_tags():
    ''' GET method to retrieve all tags 

        Returns:
            Response (JSON): A list of all tags stored in tag_table.
    '''
    connection, cursor = get_cursor()
    tags = database.view_all_tags(cursor)
    connection.close()
    return jsonify(tags)

@app.route('/pantry/current_tags', methods=['GET'])
def get_current_tags():
    ''' GET method to retrieve currently used tags 

        Returns:
            Response (JSON): A list of item tags stored in junction_table.
    '''
    connection, cursor = get_cursor()
    current_tags = database.view_item_tags(cursor)
    connection.close()
    return jsonify(current_tags)

@app.route('/pantry/current_tags/<string:tag>', methods=['GET'])
def get_item_with_tag(tag : str):
    ''' GET method to retrieve items with specific tag

        Returns:
            Response (JSON): Items with desired tag 
    '''
    connection, cursor = get_cursor()
    item = database.view_item_tags(cursor, tag)
    connection.close()
    return jsonify(item)

@app.route('/pantry/names', methods=['GET'])
def get_names():
    ''' GET method to retrieve all names 

        Returns:
            Response (JSON): A list of all names stored in main_table.
    '''
    connection, cursor = get_cursor()
    names = database.view_all_names(cursor)
    connection.close()
    return jsonify(names)

# @app.route('/pantry/names/<string:name>', methods=['GET'])
# def get_item_with_name(name : str):
    ''' GET method to retrieve items with specific name

        Returns:
            Response (JSON): Items with desired name 
    '''
    # connection, cursor = get_cursor()
    # item = database.
    # connection.close()
    # return jsonify(item)

@app.route('/pantry/brands', methods=['GET'])
def get_brands():
    ''' GET method to retrieve all brands 

        Returns:
            Response (JSON): A list of all brands stored in main_table.
    '''
    connection, cursor = get_cursor()
    brands = database.view_all_brands(cursor)
    connection.close()
    return jsonify(brands)

# @app.route('/pantry/brands/<string:brand>', methods=['GET'])
# def get_item_with_brand(brand : str):
    ''' GET method to retrieve items with specific brand

        Returns:
            Response (JSON): Items with desired brand 
    '''
    # connection, cursor = get_cursor()
    # item = database.
    # connection.close()
    # return jsonify(item)

# @app.route('/pantry/inventory/<int:id>', methods=['GET'])
# def get_item_with_id(id : int):
    ''' GET method to retrieve items with specific id

        Returns:
            Response (JSON): Items with desired id 
    '''
    # connection, cursor = get_cursor()
    # item = database.
    # connection.close()
    # return jsonify(item)

# --------------------------------------------------
# POST methods
# --------------------------------------------------
@app.route('/pantry/inventory/new_item', methods=['POST'])
def add_item():
    ''' Add new item to the inventory

        Returns:
            Response (JSON): Message confirming new item added with item
    '''
    id = request.form.get('id')
    name = request.form.get('name')
    brand = request.form.get('brand')
    quantity = request.form.get('quantity')
    tags = request.form.get('tags', '').split(',')
    image = request.form.get('image')
    # image = request.file.get(image) # TODO: Handling image file (later)

    connection, cursor = get_cursor()
    new_item = database.add_new_item(cursor, name, brand, id, quantity, image, tags)
    connection.commit()
    connection.close()
    return jsonify({'message': 'Item added!', 'item': new_item}), 201

# --------------------------------------------------
# PATCH methods
# --------------------------------------------------
@app.route('/pantry/inventory/<int:id>', methods=['PATCH'])
def update_quantity(id):
    quantity = request.form.get('quantity')
    # TODO: Handle option to increase/decrease quantity
    connection, cursor = get_cursor()

    # From Camile's database
    cursor.execute(f'SELECT quantity FROM main_table WHERE id == {id}')
    old_quantity = cursor.fetchall()[0][0]
    new_quantity = int(old_quantity) + quantity

    if new_quantity < 0:
        return jsonify({'error': 'Item quantity can\'t go below 0.', 'Current quantity': old_quantity}), 400

    update = database.update_item(cursor, id, quantity)
    connection.commit()
    connection.close()
    return jsonify({'message': 'Item added!', 'item': new_item}), 201

if __name__ == '__main__':
    app.run(debug=True)