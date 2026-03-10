from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from auth import requires_roles
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database import db as database

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['https://piratepantry.com', 'https://www.piratepantry.com', 'https://dev.piratepantry.com', 'http://localhost:5173'], supports_credentials=True)

# --------------------------------------------------
# GET methods (from database)
# --------------------------------------------------
@app.route('/api/table', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_table():
    ''' GET method to retrieve the pantry table

        Returns:
            Response (JSON): A list of all pantry items stored in products.
    '''
    pantry = database.view_table()
    return jsonify(pantry)

@app.route('/api/table/all_names', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_all_names():
    ''' GET method to retrieve all names 

        Returns:
            Response (JSON): A list of all names stored in products.
    '''
    names = database.view_all_names()
    return jsonify(names)

@app.route('/api/table/all_brands', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_all_brands():
    ''' GET method to retrieve all brands 

        Returns:
            Response (JSON): A list of all brands stored in products.
    '''
    brands = database.view_all_brands()
    return jsonify(brands)

@app.route('/api/table/all_tags', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_all_tags():
    ''' GET method to retrieve all tags 

        Returns:
            Response (JSON): A list of all tags stored in tags.
    '''
    tags = database.view_all_tags()
    return jsonify(tags)

# --------------------------------------------------
# GET methods (from inventory)
# --------------------------------------------------

@app.route('/api/inventory', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_inventory():
    ''' GET method to retrieve the pantry inventory with quantity > 0

        Returns:
            Response (JSON): A list of all pantry items in products with quantity > 0.
    '''
    inventory = database.view_pantry_inventory()
    return jsonify(inventory)

@app.route('/api/inventory/names', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_names():
    ''' GET method to retrieve available names in pantry

        Returns:
            Response (JSON): A list of names stored in products.
    '''
    names = database.view_pantry_names()
    return jsonify(names)

@app.route('/api/inventory/brands', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_brands():
    ''' GET method to retrieve available brands in pantry

        Returns:
            Response (JSON): A list of brands stored in products.
    '''
    brands = database.view_pantry_brands()
    return jsonify(brands)

@app.route('/api/inventory/tags', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_tags():
    ''' GET method to retrieve currently used tags 

        Returns:
            Response (JSON): A list of item tags stored in product_tags.
    '''
    current_tags = database.view_pantry_tags()
    return jsonify(current_tags)

# --------------------------------------------------
# POST methods
# --------------------------------------------------
@app.route('/api/table/add/item', methods=['POST'])
@requires_roles('trusted', 'admin')
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

    try:
        new_item = database.add_item(name, brand, id, quantity, image, tags)
        return jsonify({'message': 'Item added!', 'item': new_item}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/table/add/item/tags', methods=['POST'])
@requires_roles('trusted', 'admin')
def add_tags_to_table():
    ''' Add new tags to the table

        Returns:
            Response (JSON): New tags added to tags
    '''
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'})
    
    new_tag = [t.strip() for t in data.get('tags', '').split(',') if t.strip()]
    
    try:
        add_tag = database.add_tags_to_table(new_tag)

        return jsonify({'message': 'Tags added!', 'tags': add_tag}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --------------------------------------------------
# PATCH method (update items)
# --------------------------------------------------
# @app.route('/api/table/update/<int:id>', methods=['PATCH'])
# @requires_roles('trusted', 'admin', 'user')
# def update_item(current_user=None):
#     data = request.get_json()
#
#     if not data:
#         return jsonify({'error': 'Invalid JSON'})
#
#     # TODO: check with Camile for this method
#     id = data.get('id', type=int)
#     quantity = data.get('quantity', type=int)
#
#     if not id or not quantity:
#         return jsonify({'error': 'Missing required fields: ID, Name.' })
#
#     if quantity == 0:
#         return jsonify({'error': 'Updated quantity needs to be above 0.'}), 400
#
#     connection, cursor = get_cursor()
#     if not database.in_table(cursor, id):
#         connection.close()
#         return jsonify({'error': 'Item not found.'}), 400
#
#     updated_item = database.update_item(cursor, id, quantity)
#
#     if updated_item == "Invalid quantity":
#         connection.close()
#         return jsonify({'error': 'New quantity can\'t be negative.'}), 400
#
#     database.save(connection)
#     connection.close()
#     return jsonify({'message': 'Item updated!', 'New quantity': updated_item}), 201

# --------------------------------------------------
# PATCH method (checkout)
# --------------------------------------------------
@app.route('/api/inventory/checkout/<int:id>', methods=['PATCH'])
@requires_roles('admin', 'trusted', 'user')
def checkout_item(id: int):
    ''' PATCH method to check item out (decrease item's quantity)

        Returns:
            Response (JSON): A list of checked out items.
    '''
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'})
    
    quantity = data.get('quantity', type=int)

    if not quantity:
        return jsonify({'error': 'Missing required field: Quantity.'}), 400
    
    if quantity == 0:
        return jsonify({'error': 'Checkout quantity needs to be above 0.'}), 400
    
    if not database.in_table(id):
        return jsonify({'error': 'Item not found.'}), 400
    
    checkout = database.checkout_item(id, quantity)
    if checkout == "Invalid quantity":
        return jsonify({'error': 'New quantity can\'t be negative.'}), 400

    return jsonify({'message': 'Item checked out!', 'New quantity': checkout}), 201

# --------------------------------------------------
# GET methods (item search)
# --------------------------------------------------

@app.route('/api/pantry/item_information/<int:id>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_all_info(id: int):
    ''' GET method to retrieve all info for an item

        Returns:
            Response (JSON): Item with all its information
    '''
    info = database.get_all_info(id)
    return jsonify(info)

@app.route('/api/inventory/search/name/<string:name>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_name(name: str):
    ''' GET method to retrieve items with specific name in inventory

        Returns:
            Response (JSON): Items with desired name 
    '''
    item = database.search_pantry_by_name(name)
    return jsonify(item)

@app.route('/api/inventory/search/brand/<string:brand>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_brand(brand: str):
    ''' GET method to retrieve items with specific brand in inventory

        Returns:
            Response (JSON): Items with desired brand 
    '''
    item = database.search_pantry_by_brand(brand)
    return jsonify(item)

@app.route('/api/inventory/search/id/<int:id>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_id(id: int):
    ''' GET method to retrieve items with specific id

        Returns:
            Response (JSON): Items with desired id 
    '''
    item = database.search_pantry_by_id(id)
    return jsonify(item)

@app.route('/api/inventory/search/tags/<string:tag>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_tag(tag: str):
    ''' GET method to retrieve items with specific tag

        Returns:
            Response (JSON): Items with desired tag 
    '''
    item = database.search_pantry_by_tag(tag)
    return jsonify(item)

# --------------------------------------------------
# DELETE methods (item removal)
# --------------------------------------------------
@app.route('/api/table/delete/item/<int:id>', methods=['DELETE'])
@requires_roles('trusted', 'admin')
def delete_item(id: int):
    ''' DELETE method to remove an item from the pantry (permanently)

        Returns:
            Response (JSON): Item removed
    '''
    deleted_item = database.delete_item(id)
    return jsonify(deleted_item)

@app.route('/api/table/delete/tag/<string:tag>', methods=['DELETE'])
@requires_roles('trusted', 'admin')
def delete_tag(tag: str):
    ''' DELETE method to remove a tag from the pantry (permanently)

        Returns:
            Response (JSON): Tag removed
    '''
    deleted_tag = database.delete_tag(tag)
    return jsonify(deleted_tag)


if __name__ == '__main__':
    app.run(debug=True)
