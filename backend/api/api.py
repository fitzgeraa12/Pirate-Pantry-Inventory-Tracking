from typing import Any, Optional, cast

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

from pydantic import BaseModel, ValidationError, field_validator
from auth import requires_roles
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import database.db as database
from database.db import query 
# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['https://piratepantry.com', 'https://www.piratepantry.com', 'https://dev.piratepantry.com', 'http://localhost:5173'], supports_credentials=True)


# --------------------------------------------------
# Helper fns
# --------------------------------------------------

def parse_symbol_expr(raw: str, member_name: str, alias: Optional[str]) -> tuple[str, str]:
    ''' Parse symbol expression string into SQL condition and param.
        Uses table alias if provided (e.g. 'p' for 'p.name'), or no alias if None.

        Supported syntax:
            Cheerios   -> exact match
            *Cheerios* -> contains
            Cheerios*  -> starts with
            *Cheerios  -> ends with

        Returns:
            tuple[str, str]: (SQL condition, param value)
    '''
    starts_wild = raw.startswith('*')
    ends_wild = raw.endswith('*')
    stripped = raw.strip('*')

    if not stripped:
        raise ValueError(f'Invalid symbol expression for {member_name}: must contain at least one valid character (not *)')

    col = f'{alias}.{member_name}' if alias else member_name

    if starts_wild and ends_wild:
        return f'{col} LIKE ?', f'%{stripped}%'
    elif ends_wild:
        return f'{col} LIKE ?', f'{stripped}%'
    elif starts_wild:
        return f'{col} LIKE ?', f'%{stripped}'
    else:
        return f'{col} = ?', raw


def parse_quantity_expr(raw: str) -> tuple[list[str], list[Any]]:
    ''' Parse quantity range string into SQL conditions and params.

        Supported syntax:
            7      -> exactly 7
            5:10   -> between 5 and 10 inclusive
            5:     -> at least 5
            :10    -> at most 10

        Returns:
            tuple[list[str], list[Any]]: (SQL conditions, params)
    '''
    conditions: list[str] = []
    params: list[Any] = []

    if ':' in raw:
        parts = raw.split(':', 1)
        low = parts[0].strip()
        high = parts[1].strip()

        if not low and not high:
            raise ValueError('Invalid quantity expression: must provide at least one bound')

        if low:
            if not low.lstrip('-').isdigit():
                raise ValueError(f'Invalid quantity expression: "{low}" is not an integer')
            conditions.append('p.quantity >= ?')
            params.append(int(low))
        if high:
            if not high.lstrip('-').isdigit():
                raise ValueError(f'Invalid quantity expression: "{high}" is not an integer')
            conditions.append('p.quantity <= ?')
            params.append(int(high))
    else:
        if not raw.lstrip('-').isdigit():
            raise ValueError(f'Invalid quantity expression: "{raw}" is not an integer')
        conditions.append('p.quantity = ?')
        params.append(int(raw))

    return conditions, params


def validate_symbol(name: str, symbol_name: str) -> Optional[str]:
    ''' Validate a symbol. Returns an error string if invalid, None if valid. '''
    if '*' in name:
        return f'\'{symbol_name}\' cannot contain *'
    if not name.strip():
        return f'\'{symbol_name}\' cannot be whitespace'
    if '  ' in name:
        return f'\'{symbol_name}\' cannot contain consecutive whitespace'
    if not re.match(r'^[^\W_]( ?[^\W_])*$', name, re.UNICODE):
        return f'\'{symbol_name}\' can only contain alphanumeric characters and spaces'
    return None


# --------------------------------------------------
# Products
# --------------------------------------------------

class GetProductsSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[str] = None
    image_link: Optional[str] = None
    tags: Optional[str] = None

@app.route('/products', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_products():
    ''' GET method to retrieve products, optionally filtered by query parameters.
        All filters are combined with AND logic.

        Query parameters (all optional):
            - id (int): Exact product ID
            - name (str): With wildcard support:
                name=Cheerios   -> exact match
                name=*Cheerios* -> contains
                name=Cheerios*  -> starts with
                name=*Cheerios  -> ends with
            - brand (str): With wildcard support:
                brand=General Mills   -> exact match
                brand=*General Mills* -> contains
                brand=General Mills*  -> starts with
                brand=*General Mills  -> ends with
            - quantity (str): With range support:
                quantity=7      -> exactly 7
                quantity=5:10   -> between 5 and 10 inclusive
                quantity=5:     -> at least 5
                quantity=:10    -> at most 10
            - image_link (str): Exact image link match
            - tags (str): Comma-separated list of tags to filter by

        Returns:
            Response (JSON): A list of matching products.
    '''
    try:
        query = GetProductsSchema.model_validate(request.args.to_dict())
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    tag_list = [t.strip() for t in query.tags.split(',') if t.strip()] if query.tags else []

    conditions: list[str] = []
    params: list[Any] = []

    try:
        if query.quantity:
            q_conditions, q_params = parse_quantity_expr(query.quantity)
            conditions.extend(q_conditions)
            params.extend(q_params)
        if query.name:
            condition, param = parse_symbol_expr(query.name, 'name', 'p')
            conditions.append(condition)
            params.append(param)
        if query.brand:
            condition, param = parse_symbol_expr(query.brand, 'brand', 'p')
            conditions.append(condition)
            params.append(param)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    if query.id:
        conditions.append('p.id = ?')
        params.append(query.id)
    if query.image_link:
        conditions.append('p.image_link = ?')
        params.append(query.image_link)

    where = ('WHERE ' + ' AND '.join(conditions)) if len(conditions) > 0 else ''

    if tag_list:
        placeholders = ', '.join('?' for _ in tag_list)
        sql = f'''
            SELECT DISTINCT p.* FROM products p
            JOIN product_tags pt ON p.id = pt.product_id
            {where}
            {'AND' if conditions else 'WHERE'} pt.tag_label IN ({placeholders})
        '''
        params.extend(tag_list)
    else:
        sql = f'SELECT * FROM products p {where}'

    products = database.query(sql, params if len(params) > 0 else None)
    return jsonify(products)

class PostProductSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[int] = None
    image_link: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator('name')
    @classmethod
    def validate_name_field(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        error = validate_symbol(v, "name")
        if error:
            raise ValueError(error)
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags_field(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        for tag in v:
            error = validate_symbol(tag, 'tag')
            if error:
                raise ValueError(error)
        return v


@app.route('/products', methods=['POST'])
@requires_roles('trusted', 'admin')
def post_products():
    ''' ... '''
    data: Any = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of products'}), 400

    results: list[Any] = []
    errors: list[Any] = []

    for raw_p in cast(list[Any], data):
        try:
            p = PostProductSchema.model_validate(raw_p)
        except ValidationError as e:
            errors.append({'error': e.errors(), 'item': raw_p})
            continue

        try:
            existing = database.in_table(p.id)
            if not existing and not p.name:
                errors.append({'error': 'Name is required for new products', 'item': raw_p})
                continue

            if existing:
                new_quantity = p.quantity if p.quantity is not None else existing[0]['quantity']
                new_name = p.name if p.name is not None else existing[0]['name']
                new_brand = p.brand if p.brand is not None else existing[0]['brand']
                new_image_link = p.image_link if p.image_link is not None else existing[0]['image_link']

                database.query('''
                    INSERT INTO products (id, name, brand, quantity, image_link)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        brand = excluded.brand,
                        quantity = excluded.quantity,
                        image_link = excluded.image_link
                ''', [p.id, new_name, new_brand, new_quantity, new_image_link])

                result = database.get_all_info(p.id)

            else:
                new_quantity = p.quantity if p.quantity is not None else 0

                if p.id:
                    database.add_item(id=p.id, name=p.name, brand=p.brand, quantity=new_quantity, image_link=p.image_link)
                    result = database.get_all_info(p.id)
                    database.add_item(name=p.name, brand=p.brand, quantity=new_quantity, image_link=p.image_link)
                    result = database.query('SELECT * FROM products WHERE id = last_insert_rowid()')

            if p.tags is not None:
                result_id = result[0]['id'] if result else p.id
                database.query('DELETE FROM product_tags WHERE product_id = ?', [result_id])
                for tag in p.tags:
                    database.add_tags_to_table(tag)
                    database.query('INSERT INTO product_tags (product_id, tag_label) VALUES (?, ?)', [result_id, tag])

            if result:
                results.append(result[0])

        except Exception as e:
            errors.append({'error': str(e), 'item': raw_p})

    return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207


class DeleteProductsSchema(BaseModel):
    ids: list[int]


@app.route('/products', methods=['DELETE'])
@requires_roles('trusted', 'admin')
def delete_products():
    ''' DELETE method to remove a list of products by ID.
        Also removes all associated product_tags entries.

        Request body (JSON):
            { "ids": list[int] } - List of product IDs to delete

        Returns:
            Response (JSON): {
                "deleted": list of successfully deleted IDs,
                "errors": list of failed IDs with error messages
            }
            200 if all succeeded, 207 if some failed.
    '''
    data: Any = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    try:
        body = DeleteProductsSchema.model_validate(data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    results: list[int] = []
    errors: list[Any] = []

    for id in body.ids:
        try:
            database.delete_item(id)
            results.append(id)
        except Exception as e:
            errors.append({'error': str(e), 'id': id})

    return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207


# --------------------------------------------------
# Tags
# --------------------------------------------------

class GetTagsQuery(BaseModel):
    label: Optional[str] = None

@app.route('/tags', methods=['GET'])
@requires_roles('user', 'trusted', 'admin')
def get_tags():
    ''' GET method to retrieve tags, optionally filtered by query parameters.

        Query parameters (all optional):
            - label (str): With wildcard support:
                label=Gluten Free   -> exact match
                label=*Gluten Free* -> contains
                label=Gluten Free*  -> starts with
                label=*Gluten Free  -> ends with

        Returns:
            Response (JSON): A list of matching tags.
    '''
    try:
        query = GetTagsQuery.model_validate(request.args.to_dict())
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    conditions: list[str] = []
    params: list[Any] = []

    if query.label:
        try:
            condition, param = parse_symbol_expr(query.label, 'label', alias=None)
            conditions.append(condition)
            params.append(param)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    where = ('WHERE ' + ' AND '.join(conditions)) if len(conditions) > 0 else ''
    sql = f'SELECT * FROM tags {where}'

    tags = database.query(sql, params if len(params) > 0 else None)
    return jsonify(tags)


class PostTagsSchema(BaseModel):
    labels: list[str]

    @field_validator('labels')
    @classmethod
    def validate_labels(cls, v: list[str]) -> list[str]:
        for label in v:
            error = validate_symbol(label, 'label')
            if error:
                raise ValueError(error)
        return v


@app.route('/tags', methods=['POST'])
@requires_roles('trusted', 'admin')
def post_tags():
    ''' POST method to add a list of tags.

        Request body (JSON):
            { "labels": list[str] } - A list of tag labels to add.

        Returns:
            Response (JSON): {
                "added": list of successfully added tags,
                "errors": list of failed tags with error messages
            }
            201 if all succeeded, 207 if some failed.
    '''
    data: Any = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    try:
        body = PostTagsSchema.model_validate(data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    results: list[str] = []
    errors: list[Any] = []

    for label in body.labels:
        try:
            database.add_tags_to_table(label)
            results.append(label)
        except Exception as e:
            errors.append({'error': str(e), 'label': label})

    return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207

class DeleteTagsSchema(BaseModel):
    labels: list[str]


@app.route('/tags', methods=['DELETE'])
@requires_roles('trusted', 'admin')
def delete_tags():
    ''' DELETE method to remove a list of tags by label.
        Also removes all associated product_tags entries.

        Request body (JSON):
            { "labels": list[str] } - List of tag labels to delete

        Returns:
            Response (JSON): {
                "deleted": list of successfully deleted labels,
                "errors": list of failed labels with error messages
            }
            200 if all succeeded, 207 if some failed.
    '''
    data: Any = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    try:
        body = DeleteTagsSchema.model_validate(data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    results: list[str] = []
    errors: list[Any] = []

    for label in body.labels:
        try:
            database.delete_tag(label)
            results.append(label)
        except Exception as e:
            errors.append({'error': str(e), 'label': label})

    return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207

# --------------------------------------------------
# Remaining endpoints
# --------------------------------------------------

@app.route('/table', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_table():
    return jsonify(database.view_table())


@app.route('/table/all_names', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_all_names():
    return jsonify(database.view_all_names())


@app.route('/table/all_brands', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_all_brands():
    return jsonify(database.view_all_brands())


@app.route('/table/all_tags', methods=['GET'])
@requires_roles('trusted', 'admin')
def get_all_tags():
    return jsonify(database.view_all_tags())


@app.route('/inventory', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_inventory():
    return jsonify(database.view_pantry_inventory())


@app.route('/inventory/names', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_names():
    return jsonify(database.view_pantry_names())


@app.route('/inventory/brands', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_brands():
    return jsonify(database.view_pantry_brands())


@app.route('/inventory/tags', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_pantry_tags():
    return jsonify(database.view_pantry_tags())


@app.route('/cache_auth', methods=['POST'])
def cache_auth():
    cache_res = database.cache_auth(request.headers.get('Authorization', '').replace('Bearer ', ''))
    return jsonify({'success': cache_res})


# --------------------------------------------------
# PATCH method (update items)
# --------------------------------------------------
# @app.route('/table/update/<int:id>', methods=['PATCH'])
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

@app.route('/inventory/checkout/<int:id>', methods=['PATCH'])
@requires_roles('admin', 'trusted', 'user')
def checkout_item(id: int):
    ''' PATCH method to check item out (decrease item's quantity)

        Returns:
            Response (JSON): Updated quantity after checkout.
    '''
    data: Any = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    quantity = data.get('quantity')
    if quantity is None:
        return jsonify({'error': 'Missing required field: quantity'}), 400
    if not isinstance(quantity, int):
        return jsonify({'error': 'Quantity must be an integer'}), 400
    if quantity <= 0:
        return jsonify({'error': 'Checkout quantity must be above 0'}), 400

    if not database.in_table(id):
        return jsonify({'error': 'Item not found'}), 404

    checkout = database.checkout_item(id, quantity)
    if checkout == 'Invalid quantity':
        return jsonify({'error': "New quantity can't be negative"}), 400

    return jsonify({'message': 'Item checked out!', 'new_quantity': checkout}), 200


@app.route('/pantry/item_information/<int:id>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_all_info(id: int):
    return jsonify(database.get_all_info(id))


@app.route('/inventory/search/name/<string:name>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_name(name: str):
    return jsonify(database.search_pantry_by_name(name))


@app.route('/inventory/search/brand/<string:brand>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_brand(brand: str):
    return jsonify(database.search_pantry_by_brand(brand))


@app.route('/inventory/search/id/<int:id>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_id(id: int):
    return jsonify(database.search_pantry_by_id(id))


@app.route('/inventory/search/tags/<string:tag>', methods=['GET'])
@requires_roles('trusted', 'admin', 'user')
def get_item_by_tag(tag: str):
    return jsonify(database.search_pantry_by_tag(tag))


@app.route('/table/delete/item/<int:id>', methods=['DELETE'])
@requires_roles('trusted', 'admin')
def delete_item(id: int):
    return jsonify(database.delete_item(id))


@app.route('/table/delete/tag/<string:tag>', methods=['DELETE'])
@requires_roles('trusted', 'admin')
def delete_tag(tag: str):
    return jsonify(database.delete_tag(tag))


if __name__ == '__main__':
    app.run()
    