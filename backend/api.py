from functools import wraps
import os
import io
import re
import secrets
from typing import Any, Callable, Optional, cast
from flask import Flask, jsonify, redirect, send_file, request, g, session as flask_session
from flask_cors import CORS
from pydantic import BaseModel, ValidationError, field_validator
from common import UNSET
from misc import env_get
from database import AccessLevel, Brand, CannotDemoteOnlyAdminError, Database, LocalDatabase, Product, ProductNotFoundError, NotEnoughProductStockError, Tag, User, UserAlreadyExistsError, UserNotFoundError, normalize_email
from google_auth_oauthlib.flow import Flow # pyright: ignore[reportMissingTypeStubs]
import jwt
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import stats

import subprocess
ALLOWED_ORIGINS = ['https://piratepantry.com', 'https://www.piratepantry.com', 'https://dev.piratepantry.com']

def create_app(db: Database, is_local: bool) -> Flask:
    app = Flask(__name__)
    
    origins = ['https://piratepantry.com', 'https://www.piratepantry.com', 'https://dev.piratepantry.com', 'https://pirate-pantry-website.pages.dev']
    if is_local:
        origins.append('http://localhost:5173')
    
    CORS(app, origins=origins, supports_credentials=True)
    app.secret_key = env_get("FLASK_SECRET_KEY")
    stats.init(db)
    define_routes(app, db)
    return app

def host(db: Database, is_local: bool):
    port = int(env_get("VITE_API_PORT")) if is_local else None
    app = create_app(db, is_local)
    app.run(debug=is_local, port=port, host='0.0.0.0')

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
                if required_access_level and not session:
                    return jsonify({'error': 'Invalid session'}), 401

                user = db.get_user(session.user_id) if session and session.user_id else None
                access_level = user.access_level if session and user else None

                if required_access_level and (not access_level or not access_level.at_least(required_access_level)):
                    return jsonify({'error': 'Unauthorized'}), 403

                g.session = session
                g.user = user
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    class AddUserRequest(BaseModel):
        email: str
        access_level: AccessLevel
        id: Optional[str] = None

        @field_validator('email')
        @classmethod
        def validate_email(cls, value: str) -> str:
            normalized = normalize_email(value)
            if not normalized.endswith('@southwestern.edu'):
                raise ValueError('Email must be a southwestern.edu address')
            return normalized
    
    # --------------------------------------------------
    # Internal deploy webhook (called by GitHub Actions)
    # --------------------------------------------------

    @app.route('/internal/deploy', methods=['POST'])
    def deploy_webhook(): # pyright: ignore[reportUnusedFunction]
        token = request.headers.get('X-Deploy-Token', '')
        if not secrets.compare_digest(token, dev_token):
            return jsonify({'error': 'unauthorized'}), 401
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd=app_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }), (200 if result.returncode == 0 else 500)

    # --------------------------------------------------
    # Auth/Perms
    # --------------------------------------------------

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

        email = normalize_email(str(id_info['email']))
        if not email.endswith('@southwestern.edu'):
            return jsonify({'error': 'Unauthorized email domain'}), 403
        
        google_sub = str(id_info['sub'])
        picture: Optional[str] = id_info.get('picture')

        # Make sure user exists if in dev mode
        if isinstance(db, LocalDatabase):
            try:
                db.add_user(email, AccessLevel.ADMIN, google_sub)
            except UserAlreadyExistsError:
                pass

        user = db.get_user_by_email(email)

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
        db.store_auth_code(auth_code, session.id, picture)

        return redirect(f'{frontend_url}/auth/callback?code={auth_code}')

    @app.route('/auth/exchange', methods=['POST'])
    def auth_exchange(): # pyright: ignore[reportUnusedFunction]
        code = request.json.get('code') # pyright: ignore[reportOptionalMemberAccess]
        result = db.consume_auth_code(code)

        if not result:
            return jsonify({'error': 'Invalid or expired code'}), 401

        session_id, picture = result
        return jsonify({'session': session_id, 'picture': picture})

    @app.route('/user', methods=['GET'])
    @requires_at_least(None)
    def get_user(): # pyright: ignore[reportUnusedFunction]
        return jsonify(g.user.model_dump() if g.user else None)

    
    @app.route('/auth/whoami', methods=['GET'])
    @requires_at_least(None)
    def whoami(): # pyright: ignore[reportUnusedFunction]
        result = {'id': g.session.google_sub if g.session else None }
        return jsonify(result)

    # --------------------------------------------------
    # ADMIN only methods
    # --------------------------------------------------
    @app.route('/user', methods=['POST'])
    @requires_at_least(AccessLevel.ADMIN)
    def add_user(): # pyright: ignore[reportUnusedFunction]
        try:
            user = AddUserRequest.model_validate(request.args.to_dict())
        except ValidationError as e:
            return jsonify({'error': e.errors()}), 400
        
        try:
            new_user = db.add_user(user.email, user.access_level, user.id)
            return jsonify({'message': 'New Authorized User Added!', 'new user': new_user.model_dump()}), 201
        except UserAlreadyExistsError as e:
            return jsonify({'error': str(e)}), 409

    
    @app.route('/users', methods=['GET'])
    @requires_at_least(AccessLevel.ADMIN)
    def get_users(): # pyright: ignore[reportUnusedFunction]
        ''' GET method to view all authorized users and their roles

            Returns:
                Response (JSON): List of authorized users and their roles
        '''
        return jsonify([u.model_dump() for u in db.all_users()])

    @app.route('/user/<user_id>', methods=['PATCH'])
    @requires_at_least(AccessLevel.ADMIN)
    def update_user(user_id: str): # pyright: ignore[reportUnusedFunction]
        body: Any = request.json or {}
        try:
            new_level = AccessLevel(body.get('access_level'))
        except (ValueError, KeyError):
            return jsonify({'error': 'Invalid access_level'}), 400
        try:
            user = db.update_user_access_level(user_id, new_level, g.user.id if g.user else None)
            return jsonify(user.model_dump())
        except CannotDemoteOnlyAdminError as e:
            return jsonify({'error': str(e)}), 400
        except UserNotFoundError:
            return jsonify({'error': 'User not found'}), 404
    

    @app.route('/user/<user_id>', methods=['DELETE'])
    @requires_at_least(AccessLevel.ADMIN)
    def remove_user(user_id: str):  # pyright: ignore[reportUnusedFunction]
        ''' DELETE method to remove an authorized user

            Returns:
                Response (JSON): Confirmation message
        '''
        try:
            db.remove_user(user_id, g.user.id if g.user else None)
            return jsonify({'message': 'Authorized User Removed!'}), 200

        except UserNotFoundError:
            return jsonify({'error': 'User not found'}), 404

        except CannotDemoteOnlyAdminError as e:
            return jsonify({'error': str(e)}), 409

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        
    @app.route('/sessions', methods=['GET'])
    @requires_at_least(AccessLevel.ADMIN)
    def list_sessions(): # pyright: ignore[reportUnusedFunction]
        sessions = db.all_sessions()
        users_by_id = {u.id: u for u in db.all_users()}
        current_id = g.session.id if g.session else None
        result: list[Any] = []
        for s in sessions:
            user = users_by_id.get(s.user_id) if s.user_id else None
            result.append({
                'id': s.id,
                'user_email': user.email if user else None,
                'created_at': s.created_at,
                'expires_at': s.expires_at,
                'is_current': s.id == current_id,
            })
        return jsonify(result)

    @app.route('/session/<session_id>', methods=['DELETE'])
    @requires_at_least(AccessLevel.ADMIN)
    def revoke_session_route(session_id: str): # pyright: ignore[reportUnusedFunction]
        if g.session and g.session.id == session_id:
            return jsonify({'error': 'Cannot revoke your own session'}), 400
        db.revoke_session(session_id)
        return '', 204


    @app.route('/export', methods=['POST'])
    @requires_at_least(AccessLevel.ADMIN)
    def export_stats():
        ''' POST method to export inventory stats (e.g. total items, most common tags, etc.)
            Source: https://matplotlib.org/stable/gallery/misc/multipage_pdf.html
            
            Request body (JSON):
            - start (str): Start date in MM-DD-YYYY format
            - end (str): End date in MM-DD-YYYY format

            Returns:
                Response (JSON): Inventory stats
        '''
        body: Any = request.json or {}
        start = body.get('start')
        end = body.get('end')
        if not start or not end:
            return jsonify({'error': 'Both start and end date are required.'}), 400
        try:
            # Total number of items checked out 
            total_fig  = stats.total_range(start, end)
            # Top 10 items that got checked out 
            top_fig    = stats.top_item(start, end)
            # Percentage of item tags checked out weekly (pie chart)
            tags_fig   = stats.tag_range(start, end)
            # Number of checkouts per day
            daily_fig  = stats.checkout_daily(start, end)
            # Number of checkouts per hour (separate bar graphs for each day)
            hourly_fig = stats.checkout_hourly(start, end) 
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        try:
            buffer = io.BytesIO()
            with PdfPages(buffer) as pdf:
                for fig in [total_fig, top_fig, tags_fig, daily_fig, hourly_fig]:
                    if fig:
                        pdf.savefig(fig)
                        plt.close(fig)
            buffer.seek(0)
            return send_file(buffer, as_attachment=True,
                            download_name=f'Pirate_Pantry_Stats_{start}_to_{end}.pdf',
                            mimetype='application/pdf')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # --------------------------------------------------
    # Settings
    # --------------------------------------------------

    ALLOWED_SETTINGS = {'login_timeout_days', 'page_size'}

    @app.route('/settings', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_settings(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.get_all_settings())

    @app.route('/settings', methods=['PATCH'])
    @requires_at_least(AccessLevel.TRUSTED)
    def update_settings(): # pyright: ignore[reportUnusedFunction]
        body: Any = request.json or {}
        updated = {}
        for key, value in body.items():
            if key not in ALLOWED_SETTINGS:
                return jsonify({'error': f'Unknown setting: {key}'}), 400
            db.update_setting(key, str(value))
            updated[key] = str(value)
        return jsonify(updated)

    # --------------------------------------------------
    # Product
    # --------------------------------------------------

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
                - page (int): Page number, 1-indexed (default: 1)
                - page_size (int): Number of results per page (default: 20)

            Returns:
                Response (JSON): A paginated list of matching products.
        '''
        class GetProductsSchema(BaseModel):
            search: Optional[str] = None
            id: Optional[int] = None
            name: Optional[str] = None
            brand: Optional[str] = None
            quantity: Optional[str] = None
            image_link: Optional[str] = None
            tags: Optional[str] = None
            page: int = 1
            page_size: int = 20

        with db.transaction():
            print(request.args.to_dict())
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

            if products_query.search:
                like = f"%{products_query.search}%"
                conditions.append("""
                                  (p.name LIKE?
                                  OR p.brand LIKE ?
                                  OR CAST(p.id AS TEXT) LIKE?)
                                  """)
                params.extend([like,like,like])
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

            where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

            filter_params = params.copy()

            if tag_list:
                placeholders = ', '.join('?' for _ in tag_list)
                base_sql = f'''
                    FROM products p
                    JOIN product_tags pt ON p.id = pt.product_id
                    {where}
                    {'AND' if conditions else 'WHERE'} pt.tag_label IN ({placeholders})
                '''
                filter_params.extend(tag_list)
            else:
                base_sql = f'FROM products p {where}'

            total = db.query(f'SELECT COUNT(DISTINCT p.id) as total {base_sql}', filter_params)[0]['total']

            offset = (products_query.page - 1) * products_query.page_size
            paginated_params = filter_params + [products_query.page_size, offset]
            sql = f'SELECT DISTINCT p.* {base_sql} LIMIT ? OFFSET ?'

            products = Product.query_and_include_tags(db, sql, paginated_params)

            return jsonify({
                'data': [p.model_dump() for p in products],
                'total': total,
                'total_pages': (total + products_query.page_size - 1) // products_query.page_size,
            })

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

        with db.transaction():
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
        
    @app.route('/products', methods=['DELETE'])
    @requires_at_least(AccessLevel.TRUSTED)
    def delete_products(): # pyright: ignore[reportUnusedFunction]
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
        class DeleteProductsSchema(BaseModel):
            ids: list[int]

        with db.transaction():
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
                    db.query('DELETE FROM product_tags WHERE product_id = ?', [id])
                    db.query('DELETE FROM products WHERE id = ?', [id])
                    results.append(id)
                except Exception as e:
                    errors.append({'error': str(e), 'id': id})

            return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207

    @app.route('/products/checkout', methods=['PATCH'])
    # @requires_at_least(AccessLevel.TRUSTED)
    def checkout_products(): # pyright: ignore[reportUnusedFunction]
        ''' PATCH method to check items out (decrease items' quantities)

            Returns:
                Response (JSON): Updated quantity for each item after checkout
        '''
        class CheckoutProductSchema(BaseModel):
            id: int
            amount: int

        class CheckoutProductsSchema(BaseModel):
            products: list[CheckoutProductSchema]
        
        with db.transaction():
            data: Any = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            try:
                body = CheckoutProductsSchema.model_validate(data)
            except ValidationError as e:
                return jsonify({'error': e.errors()}), 400
            
            updated_products = []
            products = body.products
            checkout_id = stats.next_checkout_id()

            for product in products:
                id = product.id
                existing = db.product_from_id(id)

                old_quantity = existing.quantity
                new_quantity = old_quantity - product.amount

                if product.amount > existing.quantity:
                    return jsonify({'error': NotEnoughProductStockError(id, product.amount, old_quantity)}), 400

                db.query('UPDATE products SET quantity = ? WHERE id = ?', [new_quantity, id])
                updated_products.append({
                    'id': id,
                    'quantity': new_quantity
                })
                
                stats.new_checkout(
                    checkout_id=checkout_id,
                    id=existing.id,
                    name=existing.name,
                    brand=existing.brand,
                    num_checked_out=product.amount
                )

            return jsonify({'quantities': updated_products}), 200

    # @app.route('/products/all', methods=['GET'])
    # @requires_at_least(AccessLevel.TRUSTED)
    # def get_all_products(): # pyright: ignore[reportUnusedFunction]
    #     return jsonify(db.all_products())

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
    
    # --------------------------------------------------
    # Tags
    # --------------------------------------------------

    @app.route('/tags', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_tags(): # pyright: ignore[reportUnusedFunction]
        ''' GET method to retrieve tags, optionally filtered by query parameters.

            Query parameters (all optional):
                - label (str): Support for `%` (wildcard) and `_` (single-char wildcard)

            Returns:
                Response (JSON): A list of matching tags.
        '''
        class GetTagsQuery(BaseModel):
            label: Optional[str] = None
            page: int = 1
            page_size: int = 20

        try:
            tags_query = GetTagsQuery.model_validate(request.args.to_dict())
        except ValidationError as e:
            return jsonify({'error': e.errors()}), 400

        conditions: list[str] = []
        params: list[Any] = []

        if tags_query.label:
            conditions.append('t.label LIKE ?')
            params.append(tags_query.label)

        where = ('WHERE ' + ' AND '.join(conditions)) if len(conditions) > 0 else ''

        filter_params = params.copy()

        offset = (tags_query.page - 1) * tags_query.page_size
        sql = f'SELECT * FROM tags {where} LIMIT ? OFFSET ?'
        params.extend([tags_query.page_size, offset])

        tags = db.query_and_map_rows(
            sql,
            lambda row: Tag(**row),
            params
        )

        total = db.query(f'SELECT COUNT(*) as total FROM tags {where}', filter_params)[0]['total']

        return jsonify({
            'data': [t.model_dump() for t in tags],
            'total': total,
            'total_pages': (total + tags_query.page_size - 1) // tags_query.page_size,
        })

    @app.route('/tags', methods=['POST'])
    @requires_at_least(AccessLevel.TRUSTED)
    def post_tags(): # pyright: ignore[reportUnusedFunction]
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
                db.query('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', [label])
                results.append(label)
            except Exception as e:
                errors.append({'error': str(e), 'label': label})

        return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207

    @app.route('/tags', methods=['DELETE'])
    @requires_at_least(AccessLevel.TRUSTED)
    def delete_tags(): # pyright: ignore[reportUnusedFunction]
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
        class DeleteTagsSchema(BaseModel):
            labels: list[str]

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
                db.query('DELETE FROM product_tags WHERE tag_label = ?', [label])
                db.query('DELETE FROM tags WHERE label = ?', [label])
                results.append(label)
            except Exception as e:
                errors.append({'error': str(e), 'label': label})

        return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207

    # --------------------------------------------------
    # Brands
    # --------------------------------------------------

    @app.route('/brands', methods=['GET'])
    @requires_at_least(AccessLevel.TRUSTED)
    def get_brands(): # pyright: ignore[reportUnusedFunction]
        ''' GET method to retrieve brands, optionally filtered by query parameters.

            Query parameters (all optional):
                - name (str): Support for `%` (wildcard) and `_` (single-char wildcard)

            Returns:
                Response (JSON): A list of matching brands.
        '''
        class GetBrandsQuery(BaseModel):
            name: Optional[str] = None
            page: int = 1
            page_size: int = 20

        with db.transaction():
            try:
                brands_query = GetBrandsQuery.model_validate(request.args.to_dict())
            except ValidationError as e:
                return jsonify({'error': e.errors()}), 400

            conditions: list[str] = []
            params: list[Any] = []

            if brands_query.name:
                conditions.append('b.name LIKE ?')
                params.append(brands_query.name)

            where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

            filter_params = params.copy()

            offset = (brands_query.page - 1) * brands_query.page_size
            sql = f'SELECT * FROM brands b {where} LIMIT ? OFFSET ?'
            params.extend([brands_query.page_size, offset])

            brands = db.query_and_map_rows(
                sql,
                lambda row: Brand(**row),
                params
            )

            total = db.query(f'SELECT COUNT(*) as total FROM brands b {where}', filter_params)[0]['total']

            return jsonify({
                'data': [b.model_dump() for b in brands],
                'total': total,
                'total_pages': (total + brands_query.page_size - 1) // brands_query.page_size,
            })
    
    @app.route('/brands', methods=['POST'])
    @requires_at_least(AccessLevel.TRUSTED)
    def post_brands(): # pyright: ignore[reportUnusedFunction]
        ''' POST method to add a list of brands.

            Request body (JSON):
                { "names": list[str] } - A list of brand names to add.

            Returns:
                Response (JSON): {
                    "added": list of successfully added brands,
                    "errors": list of failed brands with error messages
                }
                201 if all succeeded, 207 if some failed.
        '''
        class PostTagsSchema(BaseModel):
            names: list[str]

            @field_validator('names')
            @classmethod
            def validate_names(cls, v: list[str]) -> list[str]:
                for name in v:
                    error = validate_symbol(name, 'name')
                    if error:
                        raise ValueError(error)
                return v

        data: Any = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        try:
            body = PostTagsSchema.model_validate(data)
        except ValidationError as e:
            return jsonify({'error': e.errors()}), 400

        results: list[str] = []
        errors: list[Any] = []

        for name in body.names:
            try:
                db.query('INSERT INTO brands (name) VALUES (?) ON CONFLICT (label) DO NOTHING', [name])
                results.append(name)
            except Exception as e:
                errors.append({'error': str(e), 'name': name})

        return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207

    @app.route('/brands', methods=['DELETE'])
    @requires_at_least(AccessLevel.TRUSTED)
    def delete_brands(): # pyright: ignore[reportUnusedFunction]
        ''' DELETE method to remove a list of brands by name.

            Request body (JSON):
                { "names": list[str] } - List of brand names to delete

            Returns:
                Response (JSON): {
                    "deleted": list of successfully deleted names,
                    "errors": list of failed names with error messages
                }
                200 if all succeeded, 207 if some failed.
        '''
        class DeleteBrandsSchema(BaseModel):
            names: list[str]

        data: Any = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        try:
            body = DeleteBrandsSchema.model_validate(data)
        except ValidationError as e:
            return jsonify({'error': e.errors()}), 400

        results: list[str] = []
        errors: list[Any] = []

        for name in body.names:
            try:
                db.query('DELETE FROM brands WHERE name = ?', [name])
                results.append(name)
            except Exception as e:
                errors.append({'error': str(e), 'name': name})

        return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207

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

def log(data: Any):
    print(data)
    pass # TODO: logging
