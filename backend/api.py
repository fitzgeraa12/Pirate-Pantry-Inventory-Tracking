from functools import wraps
import os
import re
import secrets
from typing import Any, Callable, Optional, cast
from flask import Flask, jsonify, redirect, request, g, session as flask_session
from flask_cors import CORS
from pydantic import BaseModel, ValidationError, field_validator
from backend.common import UNSET
from misc import env_get
from database import AccessLevel, Database, Product, ProductNotFoundError, User, UserAlreadyExistsError
from google_auth_oauthlib.flow import Flow # pyright: ignore[reportMissingTypeStubs]
import jwt
import requests

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
ALLOWED_ORIGINS = ['https://piratepantry.com', 'https://www.piratepantry.com', 'https://dev.piratepantry.com']

def create_app(db: Database, is_local: bool) -> Flask:
    app = Flask(__name__)
    
    origins = ['https://piratepantry.com', 'https://www.piratepantry.com', 'https://dev.piratepantry.com']
    if is_local:
        origins.append('http://localhost:5173')
    
    CORS(app, origins=origins, supports_credentials=True)
    app.secret_key = env_get("FLASK_SECRET_KEY")
    define_routes(app, db)
    return app

def host(db: Database, is_local: bool):
    port = int(env_get("VITE_API_PORT")) if is_local else None
    app = create_app(db, is_local)
    app.run(debug=is_local, port=port, host='0.0.0.0')

def log(data: Any):
    print(data)
    pass # TODO: actual logging system

def define_routes(app: Flask, db: Database):
    dev_token = env_get("DEV_TOKEN")
    frontend_port = os.environ.get("WEBSITE_PORT")
    frontend_url = f"{env_get('WEBSITE_URL')}:{frontend_port}" if frontend_port else env_get('WEBSITE_URL')
    backend_port = os.environ.get("VITE_API_PORT")
    backend_url = f"{env_get('VITE_API_URL')}:{backend_port}" if backend_port else env_get('VITE_API_URL')
    google_redirect_uri = f"{backend_url}/auth/google/callback"
    google_client_id = env_get("VITE_GOOGLE_CLIENT_ID")
    google_client_secret = env_get("GOOGLE_CLIENT_SECRET")
    flow_config: dict[str, dict[str, Any]] = {
        "web": {
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "redirect_uris": [google_redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }

    def requires_at_least(required_access_level: Optional[AccessLevel]):
        def decorator(fn: Callable[..., Any]):
            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any):
                token = request.headers.get("Authorization")
                if not token:
                    return jsonify({'error': 'No token found.'}), 401

                if token == dev_token:
                    g.session = None
                    g.user = User.DEV
                    return fn(*args, **kwargs)

                session = db.get_auth_session(token)
                if not session:
                    return jsonify({'error': 'Invalid session'}), 401

                user = db.get_user(session.user_id) if session.user_id else None
                access_level = user.access_level if user else None

                if required_access_level and (not access_level or not access_level.at_least(required_access_level)):
                    return jsonify({'error': 'Unauthorized'}), 403

                g.session = session
                g.user = user
                return fn(*args, **kwargs)
            return wrapper
        return decorator
    
    @app.route('/products/all', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_all_products(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_products())


    @app.route('/products/all/names', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_all_product_names(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_names())


    @app.route('/products/all/brands', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_all_product_brands(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_brands())


    @app.route('/products/all/tags', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_all_product_tags(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_tags())


    @app.route('/products/available', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_pantry_inventory(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_products())


    @app.route('/products/available/names', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_pantry_names(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_names())


    @app.route('/products/available/brands', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_pantry_brands(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_brands())

    @app.route('/products/available/tags', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_pantry_tags(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_tags())
    
    @app.route('/auth/google')
    def google_auth(): # pyright: ignore[reportUnusedFunction]
        flow = Flow.from_client_config( # pyright: ignore[reportUnknownMemberType]
            flow_config,
            scopes=['openid', 'email', 'profile'],
            redirect_uri=google_redirect_uri
        )
        
        auth_url, _ = cast(tuple[str, str], flow.authorization_url( # pyright: ignore[reportUnknownMemberType]
            access_type='offline',
            prompt='consent',
        ))

        flask_session['code_verifier'] = flow.code_verifier # pyright: ignore[reportUnknownMemberType]

        return redirect(auth_url)

    @app.route('/auth/google/callback')
    def google_auth_callback(): # pyright: ignore[reportUnusedFunction]
        token_response = requests.post('https://oauth2.googleapis.com/token', data={
            'code': request.args.get('code'),
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'redirect_uri': google_redirect_uri,
            'grant_type': 'authorization_code',
            'code_verifier': flask_session.get('code_verifier'),
        })
        token_data = token_response.json()

        raw_id_token: str = str(token_data.get('id_token'))
        id_info = jwt.decode(raw_id_token, options={"verify_signature": False})

        email = str(id_info['email'])
        if not email.endswith('@southwestern.edu'):
            return jsonify({'error': 'Unauthorized email domain'}), 403
        
        google_sub = str(id_info['sub'])
        user = db.get_user(google_sub)

        if not user:
            local, domain = email.split('@')
            redacted_email = f'{local[:2]}***@{domain}'
            log(f'Visitor logged in: sub={google_sub} email={redacted_email}')
        else:
            log(f'User logged in: sub={google_sub} email={email} access_level={user.access_level}')

        refresh_token = token_data.get('refresh_token')
        if not refresh_token:
            return jsonify({'error': 'Google did not provide the expected refresh token'}), 500

        session = db.create_auth_session(
            user_id=user.id if user else None,
            google_sub=google_sub,
            refresh_token=str(refresh_token)
        )

        auth_code = secrets.token_urlsafe(64)
        db.store_auth_code(auth_code, session.id)

        return redirect(f'{frontend_url}/auth/callback?code={auth_code}')

    @app.route('/auth/exchange', methods=['POST'])
    def auth_exchange(): # pyright: ignore[reportUnusedFunction]
        code = request.json.get('code') # pyright: ignore[reportOptionalMemberAccess]
        session_id = db.consume_auth_code(code)

        if not session_id:
            return jsonify({'error': 'Invalid or expired code'}), 401
        
        return jsonify({'session': session_id})

    @app.route('/user', methods=['GET'])
    @requires_at_least(None)
    def get_user(): # pyright: ignore[reportUnusedFunction]
        return jsonify(g.user.model_dump() if g.user else None)
    
    @app.route('/user', methods=['POST'])
    @requires_at_least(AccessLevel.ADMIN)
    def add_user(): # pyright: ignore[reportUnusedFunction]
        try:
            user = User.model_validate(request.args.to_dict())
        except ValidationError as e:
            return jsonify({'error': e.errors()}), 400
        
        try:
            new_user = db.add_user(user.id, user.email, user.access_level)
            return jsonify(new_user.model_dump()), 201
        except UserAlreadyExistsError as e:
            return jsonify({'error': str(e)}), 409

    
    @app.route('/auth/whoami', methods=['GET'])
    @requires_at_least(None)
    def whoami(): # pyright: ignore[reportUnusedFunction]
        result = {'id': g.session.google_sub if g.session else None}
        return jsonify(result)

    # FIXME: remove custom wildcard behavior in name and brand
    @app.route('/products', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def query_products(): # pyright: ignore[reportUnusedFunction]
        ''' GET method to retrieve products, optionally filtered by query parameters.
            All filters are combined with AND logic.

            Query parameters (all optional):
                - id (int): Exact product ID
                - name (str): Support for `%` (wildcard) and `_` (single-char wildcard)
                - brand (str): Support for `%` (wildcard) and `_` (single-char wildcard)
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
            products_query = GetProductsSchema.model_validate(request.args.to_dict())
        except ValidationError as e:
            return jsonify({'error': e.errors()}), 400

        tag_list = [t.strip() for t in products_query.tags.split(',') if t.strip()] if products_query.tags else []

        conditions: list[str] = []
        params: list[Any] = []

        try:
            if products_query.quantity:
                q_conditions, q_params = parse_quantity_expr(products_query.quantity)
                conditions.extend(q_conditions)
                params.extend(q_params)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        if products_query.name:
            conditions.append('p.name LIKE ?')
            params.append(products_query.name)
        if products_query.brand:
            conditions.append('p.brand LIKE ?')
            params.append(products_query.brand)
        if products_query.id:
            conditions.append('p.id = ?')
            params.append(products_query.id)
        if products_query.image_link:
            conditions.append('p.image_link = ?')
            params.append(products_query.image_link)

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
    @requires_at_least(AccessLevel.TRUSTED)
    def post_products():  # pyright: ignore[reportUnusedFunction]
        class PostProductSchema(BaseModel):
            id: Optional[int] = None
            name: Optional[str] = None
            brand: Optional[str] = None  # "" = set NULL
            quantity: Optional[int] = None
            image_link: Optional[str] = None  # "" = set NULL
            tags: Optional[list[str]] = None  # [] = Remove all tags

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

        for raw_products_query in cast(list[Any], data):
            try:
                products_query = PostProductSchema.model_validate(raw_products_query)
            except ValidationError as e:
                errors.append({'error': e.errors(), 'item': raw_products_query})
                continue

            try:
                with db.transaction():
                    fields_set = products_query.model_fields_set

                    existing: Optional[Product] = None
                    if products_query.id:
                        try:
                            existing = db.product_from_id(products_query.id)
                        except ProductNotFoundError:
                            existing = None

                    if existing is None and not products_query.name:
                        errors.append({'error': 'Name is required for new products', 'item': raw_products_query})
                        continue

                    # --- normalize with "only if provided" semantics ---

                    name = (
                        products_query.name
                        if 'name' in fields_set
                        else UNSET
                    )

                    brand = (
                        None if products_query.brand == ""
                        else products_query.brand
                    ) if 'brand' in fields_set else UNSET

                    quantity = (
                        products_query.quantity
                        if ('quantity' in fields_set and products_query.quantity is not None)
                        else UNSET
                    )

                    image_link = (
                        None if products_query.image_link == ""
                        else products_query.image_link
                    ) if 'image_link' in fields_set else UNSET

                    tags = (
                        products_query.tags  # [] = clear, list = replace
                        if 'tags' in fields_set
                        else UNSET
                    )

                    if existing is None:
                        product = db.add_product(
                            id=products_query.id,
                            name=products_query.name if products_query.name is not None else "",
                            brand=None if products_query.brand == "" else products_query.brand,
                            quantity=products_query.quantity,
                            image_link=None if products_query.image_link == "" else products_query.image_link,
                            tags=products_query.tags
                        )
                    else:
                        product = db.update_product(
                            id=cast(int, products_query.id),
                            name=name,
                            brand=brand,
                            quantity=quantity,
                            image_link=image_link,
                            tags=tags
                        )

                    results.append(product.model_dump())

            except Exception as e:
                errors.append({'error': str(e), 'item': raw_products_query})

        return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207

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
    if '%' in name:
        return f'\'{symbol_name}\' cannot contain %'
    if '_' in name:
        return f'\'{symbol_name}\' cannot contain _'
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
