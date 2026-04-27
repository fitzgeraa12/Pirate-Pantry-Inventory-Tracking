from datetime import datetime
from zoneinfo import ZoneInfo
from functools import wraps
import os
import io
import re
import secrets
from typing import Any, Callable, Literal, Optional, cast
from flask import Flask, jsonify, redirect, send_file, request, g, session as flask_session
from flask_cors import CORS
from pydantic import BaseModel, ValidationError, field_validator
import backend.stats as stats
from backend.common import UNSET
from backend.misc import env_get
from backend.database import AccessLevel, Brand, CannotDemoteOnlyAdminError, Database, LocalDatabase, Product, ProductNotFoundError, NotEnoughProductStockError, Tag, User, UserAlreadyExistsError, UserNotFoundError, normalize_email
import jwt as jwt
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from werkzeug.exceptions import HTTPException
from PIL import Image, ImageDraw, ImageFont, ImageOps


import subprocess

def _pydantic_errors(e: ValidationError) -> list[dict]:
    """Pydantic v2 puts raw Exception objects in err['ctx']['error']; strip them."""
    result = []
    for err in e.errors():
        err = dict(err)
        if isinstance(err.get('ctx'), dict):
            err['ctx'] = {k: str(v) if isinstance(v, Exception) else v
                          for k, v in err['ctx'].items()}
        result.append(err)
    return result

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

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        if isinstance(e, HTTPException):
            return e
        import traceback
        tb = traceback.format_exc()
        app.logger.error(tb)
        return jsonify({'error': str(e), 'traceback': tb}), 500

    return app

def host(db: Database, is_local: bool):
    port = int(env_get("VITE_API_PORT")) if is_local else None
    app = create_app(db, is_local)
    app.run(debug=is_local, port=port, host='0.0.0.0')

def define_routes(app: Flask, db: Database):
    dev_token = env_get("DEV_TOKEN")
    frontend_port = os.environ.get("WEBSITE_PORT")
    frontend_url = f"{env_get('WEBSITE_URL').rstrip('/')}:{frontend_port}" if frontend_port else env_get('WEBSITE_URL').rstrip('/')
    backend_port = os.environ.get("VITE_API_PORT")
    backend_url = f"{env_get('VITE_API_URL')}:{backend_port}" if backend_port else env_get('VITE_API_URL')
    google_redirect_uri = f"{backend_url}/auth/google/callback"
    google_client_id = env_get("VITE_GOOGLE_CLIENT_ID")
    google_client_secret = env_get("GOOGLE_CLIENT_SECRET")

    def acquire_auth(fn: Callable[..., Any]):
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
                g.session = None
                g.user = None
                return fn(*args, **kwargs)
            g.session = session
            g.user = db.get_user(session.user_id) if session.user_id else None
            return fn(*args, **kwargs)
        return wrapper

    def requires_auth(fn: Callable[..., Any]):
        '''Requires a valid session. Sets g.session and g.user.'''
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
            g.session = session
            g.user = db.get_user(session.user_id) if session.user_id else None
            return fn(*args, **kwargs)
        return wrapper

    def requires_role(role: AccessLevel):
        '''Requires g.user to have at least the given access level. Stack after @requires_auth.'''
        def decorator(fn: Callable[..., Any]):
            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any):
                user = getattr(g, 'user', None)
                access_level = user.access_level if user else None
                if not access_level or not access_level.at_least(role):
                    return jsonify({'error': 'Unauthorized'}), 403
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
        from urllib.parse import urlencode
        params = urlencode({
            'client_id': google_client_id,
            'redirect_uri': google_redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'consent',
        })
        return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{params}')

    @app.route('/auth/google/callback')
    def google_auth_callback(): # pyright: ignore[reportUnusedFunction]
        token_response = requests.post('https://oauth2.googleapis.com/token', data={
            'code': request.args.get('code'),
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'redirect_uri': google_redirect_uri,
            'grant_type': 'authorization_code',
        })
        token_data = token_response.json()

        raw_id_token = token_data.get('id_token')
        if not raw_id_token:
            log(f'Google token exchange failed: {token_data.get("error")}: {token_data.get("error_description")}')
            return jsonify({'error': 'Google token exchange failed', 'details': token_data.get('error_description')}), 502
        id_info = jwt.decode(str(raw_id_token), options={"verify_signature": False})

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
    @requires_auth
    def get_user(): # pyright: ignore[reportUnusedFunction]
        return jsonify(g.user.model_dump() if g.user else None)

    
    @app.route('/auth/whoami', methods=['GET'])
    @acquire_auth
    def whoami(): # pyright: ignore[reportUnusedFunction]
        result = {'id': g.session.google_sub if g.session else None }
        return jsonify(result)

    # --------------------------------------------------
    # ADMIN only methods
    # --------------------------------------------------
    @app.route('/user', methods=['POST'])
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
    def add_user(): # pyright: ignore[reportUnusedFunction]
        try:
            user = AddUserRequest.model_validate(request.args.to_dict())
        except ValidationError as e:
            return jsonify({'error': _pydantic_errors(e)}), 400
        
        try:
            new_user = db.add_user(user.email, user.access_level, user.id)
            return jsonify(new_user.model_dump()), 201
        except UserAlreadyExistsError as e:
            return jsonify({'error': str(e)}), 409

    
    @app.route('/users', methods=['GET'])
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
    def get_users(): # pyright: ignore[reportUnusedFunction]
        ''' GET method to view all authorized users and their roles

            Returns:
                Response (JSON): List of authorized users and their roles
        '''
        return jsonify([u.model_dump() for u in db.all_users()])

    @app.route('/user/<user_id>', methods=['PATCH'])
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
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
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
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
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
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
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
    def revoke_session_route(session_id: str): # pyright: ignore[reportUnusedFunction]
        if g.session and g.session.id == session_id:
            return jsonify({'error': 'Cannot revoke your own session'}), 400
        db.revoke_session(session_id)
        return '', 204

    @app.route('/sessions/purge', methods=['POST'])
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
    def purge_sessions_route(): # pyright: ignore[reportUnusedFunction]
        db.purge_expired_sessions()
        return '', 204


    @app.route('/export', methods=['POST'])
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
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
            # title
            title_fig = stats.report_title(start, end)
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
            title = f'Pirate Pantry - Statistics Report ({start} - {end})'
            pages = []
            # Page 1
            pages.append([title_fig, total_fig, top_fig])
            # Page 2 
            pages.append([daily_fig, tags_fig])
            # Page 3 
            pages.append([hourly_fig])   

            page_images = []
            for figs in pages:
                figs = [f for f in figs if f]  # remove None
                if not figs:
                    continue
                figures = []

                for fig in figs:
                    buffer = io.BytesIO()
                    fig.savefig(buffer, bbox_inches='tight', facecolor='#FFFFFF')
                    buffer.seek(0)
                    figures.append(Image.open(buffer).copy())
                    plt.close(fig)

                spacing = 40
                w = max(f.width for f in figures)
                h = sum(f.height for f in figures) + spacing * (len(figures)-1)

                page = Image.new('RGB', (w,h), '#F5F5F5')
                
                y_offset = 0
                for f_ in figures:
                    f_ = ImageOps.expand(f_, border=10, fill='#DDDDDD')
                    x_offset = (w - f_.width) // 2
                    page.paste(f_, (x_offset, y_offset))   
                    y_offset += f_.height + spacing
                page_images.append(page)

            buf = io.BytesIO()
            page_images[0].save(
                buf,
                format='PDF',
                save_all=True,
                append_images=page_images[1:],
                resolution=150
            )                
            buf.seek(0)

            return send_file(buf, as_attachment=True,
                            download_name=f'Pirate_Pantry_Stats_{start}_to_{end}.pdf',
                            mimetype='application/pdf')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # --------------------------------------------------
    # Settings
    # --------------------------------------------------

    ALLOWED_SETTINGS = {'login_timeout_days', 'page_size'}

    @app.route('/settings', methods=['GET'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
    def get_settings(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.get_all_settings())

    @app.route('/settings', methods=['PATCH'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
    @requires_auth
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
            id: Optional[str] = None
            name: Optional[str] = None
            brand: Optional[str] = None
            quantity: Optional[str] = None
            image_link: Optional[str] = None
            tags: Optional[str] = None
            tag: Optional[str] = None
            page: int = 1
            page_size: int = 20
            sort_by: Literal['name', 'quantity', 'brand', 'id'] = 'name'
            sort_dir: Literal['asc', 'desc'] = 'asc'

        with db.transaction():
            print(request.args.to_dict())
            try:
                products_query = GetProductsSchema.model_validate(request.args.to_dict())
            except ValidationError as e:
                return jsonify({'error': _pydantic_errors(e)}), 400

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
                                  (p.name LIKE ?
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

            # Handle tag filtering (both exact match and LIKE search)
            has_tag_filter = bool(tag_list) or bool(products_query.tag)
            
            if has_tag_filter:
                base_sql = f'''
                    FROM products p
                    JOIN product_tags pt ON p.id = pt.product_id
                    {where}
                '''
                
                tag_conditions = []
                if tag_list:
                    placeholders = ', '.join('?' for _ in tag_list)
                    tag_conditions.append(f'pt.tag_label IN ({placeholders})')
                    filter_params.extend(tag_list)
                
                if products_query.tag:
                    tag_conditions.append('pt.tag_label LIKE ?')
                    filter_params.append(products_query.tag)
                
                tag_where = ' OR '.join(tag_conditions)
                base_sql += f"\n                    {'AND' if conditions else 'WHERE'} ({tag_where})"
            else:
                base_sql = f'FROM products p {where}'

            total = db.query(f'SELECT COUNT(DISTINCT p.id) as total {base_sql}', filter_params)[0]['total']

            _sort_col_map = {
                'name': 'p.name',
                'quantity': 'p.quantity',
                'brand': "COALESCE(p.brand, 'zzzzz')",
                'id': 'CAST(p.id AS INTEGER)',
            }
            sort_col = _sort_col_map[products_query.sort_by]
            sort_dir_sql = products_query.sort_dir.upper()
            order_by = f"ORDER BY {sort_col} {sort_dir_sql}"

            offset = (products_query.page - 1) * products_query.page_size
            paginated_params = filter_params + [products_query.page_size, offset]
            sql = f'SELECT DISTINCT p.* {base_sql} {order_by} LIMIT ? OFFSET ?'

            products = Product.query_and_include_tags(db, sql, paginated_params, order_by=order_by)

            return jsonify({
                'data': [p.model_dump() for p in products],
                'total': total,
                'total_pages': (total + products_query.page_size - 1) // products_query.page_size,
            })

    @app.route('/products', methods=['POST'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
    def post_products():  # pyright: ignore[reportUnusedFunction]
        class PostProductSchema(BaseModel):
            id: Optional[str] = None
            name: Optional[str] = None
            brand: Optional[str] = None  # "" = set NULL
            quantity: Optional[int] = None
            image_link: Optional[str] = None  # "" = set NULL
            tags: Optional[list[str]] = None  # [] = Remove all tags

            @field_validator('id')
            @classmethod
            def validate_id_field(cls, v: Optional[str]) -> Optional[str]:
                if not v:
                    return v
                if not v.isdecimal():
                    raise ValueError("id must be a numeric string")
                return v

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
                    errors.append({'error': _pydantic_errors(e), 'item': raw_products_query})
                    continue

                try:
                    with db.transaction():
                        fields_set = products_query.model_fields_set

                        existing: Optional[Product] = None
                        id_ = products_query.id
                        name_ = products_query.name
                        brand_ = products_query.brand
                        if id_ is not None and name_ is not None:
                            try:
                                existing = db.product_in_table(id_, name_, brand_)
                            except ProductNotFoundError as e:
                                print("Caught ProductNotFoundError:", e) 
                                existing = None
                            except Exception as e:
                                print("Caught something else:", type(e), e)

                        if existing is None and products_query.name is None:
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
                            if ('quantity' in fields_set and products_query.quantity is not None and products_query.quantity >= 0)
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
                            p_id = products_query.id if products_query.id else generate_id(db)
                            product = db.add_product(
                                id=p_id,
                                name=products_query.name or "",
                                brand=None if products_query.brand == "" else products_query.brand,
                                quantity=products_query.quantity,
                                image_link=None if products_query.image_link == "" else products_query.image_link,
                                tags=products_query.tags
                            )
                        else:
                            product = db.update_product(
                                id=id_,
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
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
            ids: list[str]

        with db.transaction():
            data: Any = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400

            try:
                body = DeleteProductsSchema.model_validate(data)
            except ValidationError as e:
                return jsonify({'error': _pydantic_errors(e)}), 400

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
    @requires_auth
    def checkout_products(): # pyright: ignore[reportUnusedFunction]
        ''' PATCH method to check items out (decrease items' quantities)

            Returns:
                Response (JSON): Updated quantity for each item after checkout
        '''
        class CheckoutProductSchema(BaseModel):
            id: str
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
                return jsonify({'error': _pydantic_errors(e)}), 400
            
            updated_products = []
            products = body.products

            out_of_stock = []
            for product in products:
                existing = db.product_in_table(product.id, "")
                if product.amount > existing.quantity:
                    out_of_stock.append({
                        'id': existing.id,
                        'name': existing.name,
                        'requested': product.amount,
                        'available': existing.quantity,
                    })

            if out_of_stock:
                return jsonify({'error': 'not_enough_stock', 'out_of_stock': out_of_stock}), 400

            for product in products:
                id = product.id
                existing = db.product_in_table(id, "")
                new_quantity = existing.quantity - product.amount

                db.query('UPDATE products SET quantity = ? WHERE id = ?', [new_quantity, id])
                updated_products.append({
                    'id': id,
                    'quantity': new_quantity
                })

                # stats.new_checkout(
                #     checkout_id=stats.next_checkout_id(),
                #     id=existing.id,
                #     name=existing.name,
                #     brand=existing.brand,
                #     num_checked_out=product.amount,
                #     checkout_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # )
                db.query(
                    '''
                    INSERT INTO total_checkouts
                    (checkout_id, product_id, name, brand, num_checked_out, checkout_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    [
                        stats.next_checkout_id(),
                        existing.id,
                        existing.name,
                        existing.brand or '',
                        product.amount,
                        datetime.now(ZoneInfo('America/Chicago')).strftime('%Y-%m-%d %H:%M:%S')
                    ]
                )

            return jsonify({'quantities': updated_products}), 200

    # @app.route('/products/all', methods=['GET'])
    # @requires_role(AccessLevel.TRUSTED)
    # def get_all_products(): # pyright: ignore[reportUnusedFunction]
    #     return jsonify(db.all_products())

    @app.route('/products/all/names', methods=['GET'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
    def get_all_product_names(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_names())


    @app.route('/products/all/brands', methods=['GET'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
    def get_all_product_brands(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_brands())


    @app.route('/products/all/tags', methods=['GET'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
    def get_all_product_tags(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.all_product_tags())


    @app.route('/products/available', methods=['GET'])
    @requires_auth
    def get_pantry_inventory(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_products())


    @app.route('/products/available/names', methods=['GET'])
    @requires_auth
    def get_pantry_names(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_names())


    @app.route('/products/available/brands', methods=['GET'])
    @requires_auth
    def get_pantry_brands(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_brands())

    @app.route('/products/available/tags', methods=['GET'])
    @requires_auth
    def get_pantry_tags(): # pyright: ignore[reportUnusedFunction]
        return jsonify(db.available_product_tags())
    
    # --------------------------------------------------
    # Tags
    # --------------------------------------------------

    @app.route('/tags', methods=['GET'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
            return jsonify({'error': _pydantic_errors(e)}), 400

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
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
            return jsonify({'error': _pydantic_errors(e)}), 400

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
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
            return jsonify({'error': _pydantic_errors(e)}), 400

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
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
                return jsonify({'error': _pydantic_errors(e)}), 400

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
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
            return jsonify({'error': _pydantic_errors(e)}), 400

        results: list[str] = []
        errors: list[Any] = []

        for name in body.names:
            try:
                db.query('INSERT INTO brands (name) VALUES (?) ON CONFLICT (name) DO NOTHING', [name])
                results.append(name)
            except Exception as e:
                errors.append({'error': str(e), 'name': name})

        return jsonify({'added': results, 'errors': errors}), 201 if not errors else 207

    @app.route('/brands', methods=['DELETE'])
    @requires_auth
    @requires_role(AccessLevel.TRUSTED)
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
            return jsonify({'error': _pydantic_errors(e)}), 400

        results: list[str] = []
        errors: list[Any] = []

        for name in body.names:
            try:
                db.query('DELETE FROM brands WHERE name = ?', [name])
                results.append(name)
            except Exception as e:
                errors.append({'error': str(e), 'name': name})

        return jsonify({'deleted': results, 'errors': errors}), 200 if not errors else 207

    @app.route('/reports', methods=['POST'])
    @requires_auth
    def submit_report(): # pyright: ignore[reportUnusedFunction]
        ''' POST method to submit a report.

            Request body (JSON):
                { "message": str } - The report message

            Returns:
                Response (JSON): The created report
                201 on success
        '''
        class SubmitReportSchema(BaseModel):
            message: str

            @field_validator('message')
            @classmethod
            def validate_message(cls, v: str) -> str:
                if not v.strip():
                    raise ValueError('Message cannot be empty')
                if len(v) > 1000:
                    raise ValueError('Message cannot be longer than 1000 characters')
                return v

        data: Any = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        try:
            body = SubmitReportSchema.model_validate(data)
        except ValidationError as e:
            return jsonify({'error': _pydantic_errors(e)}), 400

        report = db.add_report(g.session.user_id if g.session else None, g.user.email, body.message)
        return jsonify(report.model_dump()), 201

    @app.route('/reports', methods=['GET'])
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
    def get_reports(): # pyright: ignore[reportUnusedFunction]
        ''' GET method to retrieve all reports.

            Returns:
                Response (JSON): List of all reports
                200 on success
        '''
        reports = db.get_reports()
        return jsonify([report.model_dump() for report in reports])

    @app.route('/reports/<report_id>/resolve', methods=['POST'])
    @requires_auth
    @requires_role(AccessLevel.ADMIN)
    def resolve_report(report_id: str): # pyright: ignore[reportUnusedFunction]
        ''' POST method to mark a report as resolved.

            Returns:
                Response (JSON): Empty response
                200 on success
        '''
        db.resolve_report(report_id)
        return '', 200

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

def generate_id(db: Database) -> str:
        '''Auto-increment from 900000000000000 for item with no barcode'''
        result = db.query('SELECT MAX(CAST(id AS UNSIGNED)) as max_id FROM products WHERE CAST(id AS UNSIGNED) >= 900000000000000')
        id = result[0]['max_id']
        if id:
            return str(id + 1)
        else:
            return '900000000000000'