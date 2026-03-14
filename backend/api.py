from functools import wraps
import re
from typing import Any, Callable, Optional, cast
from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, ValidationError, field_validator
from misc import env_get
from database import AccessLevel, Database, Product, ProductNotFoundError

def create_app(db: Database, is_local: bool) -> Flask:
    app = Flask(__name__)
    if not is_local:
        CORS(app, origins=['https://piratepantry.com', 'https://www.piratepantry.com', 'https://dev.piratepantry.com', 'http://localhost:5173'], supports_credentials=True)
    
    define_routes(app, db)
    return app

def host(db: Database, is_local: bool):
    port = int(env_get("LOCAL_API_PORT"))
    app = create_app(db, is_local)
    app.run(debug=is_local, port=port)

def define_routes(app: Flask, db: Database):
    dev_token = env_get("DEV_TOKEN")

    def requires_roles(*roles: AccessLevel):
        def decorator(fn: Callable[..., Any]):
            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any):
                access_token = request.headers.get("Authorization")
                if not access_token:
                    return jsonify({'error': 'No token found.'}), 401

                if access_token != dev_token:
                    user = db.get_user(access_token)
                    access_level = user.access_level if user else AccessLevel.VISITOR
                    if access_level not in roles:
                        return jsonify({"error": "Unauthorized"}), 403
                
                return fn(*args, **kwargs)
            return wrapper
        return decorator
    
    @app.route('/products/all', methods=['GET'])
    @requires_roles(AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_all_products(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_products())


    @app.route('/products/all/names', methods=['GET'])
    @requires_roles(AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_all_product_names(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_names())


    @app.route('/products/all/brands', methods=['GET'])
    @requires_roles(AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_all_product_brands(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_brands())


    @app.route('/products/all/tags', methods=['GET'])
    @requires_roles(AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_all_product_tags(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_tags())


    @app.route('/products/available', methods=['GET'])
    @requires_roles(AccessLevel.VISITOR, AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_pantry_inventory(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_products())


    @app.route('/products/available/names', methods=['GET'])
    @requires_roles(AccessLevel.VISITOR, AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_pantry_names(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_names())


    @app.route('/products/available/brands', methods=['GET'])
    @requires_roles(AccessLevel.VISITOR, AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_pantry_brands(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_brands())


    @app.route('/products/available/tags', methods=['GET'])
    @requires_roles(AccessLevel.VISITOR, AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def get_pantry_tags(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_tags())

    @app.route('/products', methods=['GET'])
    @requires_roles(AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def query_products(): # pyright: ignore[reportUnusedFunction]
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
        class GetProductsSchema(BaseModel):
            id: Optional[int] = None
            name: Optional[str] = None
            brand: Optional[str] = None
            quantity: Optional[str] = None
            image_link: Optional[str] = None
            tags: Optional[str] = None

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

        products = Product.query_and_include_tags(db, sql, params)
        return jsonify([p.model_dump() for p in products])

    @app.route('/products', methods=['POST'])
    @requires_roles(AccessLevel.TRUSTED, AccessLevel.ADMIN)
    def post_products(): # pyright: ignore[reportUnusedFunction]
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
                with db.transaction():
                    existing: Optional[Product] = None
                    if p.id:
                        try:
                            existing = db.product_from_id(p.id)
                        except ProductNotFoundError:
                            existing = None

                    if existing is None and not p.name:
                        errors.append({'error': 'Name is required for new products', 'item': raw_p})
                        continue

                    product = db.add_product(
                        id=p.id,
                        name=p.name if p.name is not None else (existing.name if existing else ""),
                        brand=p.brand,
                        quantity=p.quantity,
                        image_link=p.image_link,
                        tags=p.tags
                    ) if existing is None else db.update_product(
                        id=cast(int, p.id),
                        name=p.name,
                        brand=p.brand,
                        quantity=p.quantity,
                        image_link=p.image_link,
                        tags=p.tags
                    )

                    results.append(product.model_dump())

            except Exception as e:
                errors.append({'error': str(e), 'item': raw_p})

        return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207

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


# # --------------------------------------------------
# # Products
# # --------------------------------------------------

# class DeleteProductsSchema(BaseModel):
#     ids: list[int]


# @app.route('/products', methods=['DELETE'])
# @requires_roles('trusted', 'admin')
# def delete_products():
#     ''' DELETE method to remove a list of products by ID.
#         Also removes all associated product_tags entries.

#         Request body (JSON):
#             { "ids": list[int] } - List of product IDs to delete

#         Returns:
#             Response (JSON): {
#                 "deleted": list of successfully deleted IDs,
#                 "errors": list of failed IDs with error messages
#             }
#             200 if all succeeded, 207 if some failed.
#     '''
#     data: Any = request.get_json()
#     if not data:
#         return jsonify({'error': 'Invalid JSON'}), 400

#     try:
#         body = DeleteProductsSchema.model_validate(data)
#     except ValidationError as e:
#         return jsonify({'error': e.errors()}), 400

#     results: list[int] = []
#     errors: list[Any] = []

#     for id in body.ids:
#         try:
#             database.query('DELETE FROM product_tags WHERE product_id = ?', [id])
#             database.query('DELETE FROM products WHERE id = ?', [id])
#             results.append(id)
#         except Exception as e:
#             errors.append({'error': str(e), 'id': id})

#     return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207


# # --------------------------------------------------
# # Tags
# # --------------------------------------------------

# class GetTagsQuery(BaseModel):
#     label: Optional[str] = None


# @app.route('/tags', methods=['GET'])
# @requires_roles('user', 'trusted', 'admin')
# def get_tags():
#     ''' GET method to retrieve tags, optionally filtered by query parameters.

#         Query parameters (all optional):
#             - label (str): With wildcard support:
#                 label=Gluten Free   -> exact match
#                 label=*Gluten Free* -> contains
#                 label=Gluten Free*  -> starts with
#                 label=*Gluten Free  -> ends with

#         Returns:
#             Response (JSON): A list of matching tags.
#     '''
#     try:
#         query = GetTagsQuery.model_validate(request.args.to_dict())
#     except ValidationError as e:
#         return jsonify({'error': e.errors()}), 400

#     conditions: list[str] = []
#     params: list[Any] = []

#     if query.label:
#         try:
#             condition, param = parse_symbol_expr(query.label, 'label', alias=None)
#             conditions.append(condition)
#             params.append(param)
#         except ValueError as e:
#             return jsonify({'error': str(e)}), 400

#     where = ('WHERE ' + ' AND '.join(conditions)) if len(conditions) > 0 else ''
#     sql = f'SELECT * FROM tags {where}'

#     tags = database.query(sql, params if len(params) > 0 else None)
#     return jsonify(tags)


# class PostTagsSchema(BaseModel):
#     labels: list[str]

#     @field_validator('labels')
#     @classmethod
#     def validate_labels(cls, v: list[str]) -> list[str]:
#         for label in v:
#             error = validate_symbol(label, 'label')
#             if error:
#                 raise ValueError(error)
#         return v


# @app.route('/tags', methods=['POST'])
# @requires_roles('trusted', 'admin')
# def post_tags():
#     ''' POST method to add a list of tags.

#         Request body (JSON):
#             { "labels": list[str] } - A list of tag labels to add.

#         Returns:
#             Response (JSON): {
#                 "added": list of successfully added tags,
#                 "errors": list of failed tags with error messages
#             }
#             201 if all succeeded, 207 if some failed.
#     '''
#     data: Any = request.get_json()
#     if not data:
#         return jsonify({'error': 'Invalid JSON'}), 400

#     try:
#         body = PostTagsSchema.model_validate(data)
#     except ValidationError as e:
#         return jsonify({'error': e.errors()}), 400

#     results: list[str] = []
#     errors: list[Any] = []

#     for label in body.labels:
#         try:
#             database.query('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', [label])
#             results.append(label)
#         except Exception as e:
#             errors.append({'error': str(e), 'label': label})

#     return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207

# class DeleteTagsSchema(BaseModel):
#     labels: list[str]


# @app.route('/tags', methods=['DELETE'])
# @requires_roles('trusted', 'admin')
# def delete_tags():
#     ''' DELETE method to remove a list of tags by label.
#         Also removes all associated product_tags entries.

#         Request body (JSON):
#             { "labels": list[str] } - List of tag labels to delete

#         Returns:
#             Response (JSON): {
#                 "deleted": list of successfully deleted labels,
#                 "errors": list of failed labels with error messages
#             }
#             200 if all succeeded, 207 if some failed.
#     '''
#     data: Any = request.get_json()
#     if not data:
#         return jsonify({'error': 'Invalid JSON'}), 400

#     try:
#         body = DeleteTagsSchema.model_validate(data)
#     except ValidationError as e:
#         return jsonify({'error': e.errors()}), 400

#     results: list[str] = []
#     errors: list[Any] = []

#     for label in body.labels:
#         try:
#             database.query('DELETE FROM product_tags WHERE tag_label = ?', [label])
#             database.query('DELETE FROM tags WHERE label = ?', [label])
#             results.append(label)
#         except Exception as e:
#             errors.append({'error': str(e), 'label': label})

#     return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207
