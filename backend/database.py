from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
import os
import time
from typing import Any, Callable, Optional, TypeVar, ClassVar, Union
import uuid
from pydantic import BaseModel
from backend.common import UNSET, Unset
from backend.misc import env_get
import requests
import sqlite3

SESSION_EXPIRY_IN_DAYS = 30

# --------------------------------------------------
# Util
# --------------------------------------------------

QueryRow = dict[str, Any]
QueryParams = list[Any]
LOCAL_STATE_DIR = os.path.join(os.path.dirname(__file__), "__local__")
LOCAL_BACKUP_PRODUCTS_PATH = os.path.join(LOCAL_STATE_DIR, "backup_products.txt")

class NotFoundError(Exception):
    def __init__(self, object: str, field: str, val: Any):
        super().__init__(f"{object} with {field} `{val}` not found")

class ProductNotFoundError(NotFoundError):
    def __init__(self, id: str):
        super().__init__("Product", "id", id)

class NotEnoughProductStockError(Exception):
    def __init__(self, id: str, amount: int, quantity: int):
        super().__init__(f"Product with id `{id}` is out of stock. Tried to check out `{amount}` items but only `{quantity}` were in stock")

class BrandNotFoundError(NotFoundError):
    def __init__(self, name: str):
        super().__init__("Brand", "name", name)

class TagNotFoundError(NotFoundError):
    def __init__(self, label: str):
        super().__init__("Tag", "label", label)

class InvalidQuantityError(Exception):
    def __init__(self, quantity: int):
        super().__init__(f"Invalid quantity `{quantity}`")

class UserNotFoundError(NotFoundError):
    def __init__(self, id: str):
        super().__init__("User", "id", id)

class UserAlreadyExistsError(Exception):
    def __init__(self, identifier: str):
        super().__init__(f"User already exists for `{identifier}`")

class CannotDemoteOnlyAdminError(Exception):
    def __init__(self):
        super().__init__("You cannot revoke your own admin privileges while you are the only admin")

# --------------------------------------------------
# Schema
# --------------------------------------------------

class Brand(BaseModel):
    name: str

class Tag(BaseModel):
    label: str

class Product(BaseModel):
    id: str
    name: str
    brand: Optional[str]
    quantity: int
    image_link: Optional[str]
    tags: list[str] = []
    
    @staticmethod
    def from_row(row: QueryRow) -> "Product":
        return Product(
            **{k: (str(v) if k == "id" else v) for k, v in row.items() if k != "tags"},
            tags=sorted(t for t in row["tags"].split(",")) if row["tags"] else []
        )
    
    @staticmethod
    def query_and_include_tags(db: "Database", sql: str, params: QueryParams = [], order_by: str = "") -> list["Product"]:
        return db.query_and_map_rows(f"""
                SELECT p.*, GROUP_CONCAT(pt.tag_label) as tags
                FROM ({sql}) p
                LEFT JOIN product_tags pt ON p.id = pt.product_id
                GROUP BY p.id
                {order_by}
            """,
            lambda row: Product.from_row(row),
            params
        )

class AccessLevel(str, Enum):
    TRUSTED = ("trusted", 1)
    ADMIN   = ("admin",   2)

    level: int

    def __new__(cls, str_value: str, int_value: int):
        obj = str.__new__(cls, str_value)
        obj._value_ = str_value
        obj.level = int_value
        return obj

    def at_least(self, other: "AccessLevel") -> bool:
        return self.level >= other.level

class User(BaseModel):
    id: str
    email: str
    access_level: AccessLevel

    DEV: ClassVar["User"]
User.DEV = User(id="dev", email="dev@piratepantry.com", access_level=AccessLevel.ADMIN)

class AuthSession(BaseModel):
    id: str
    user_id: Optional[str]
    google_sub: str
    refresh_token: str
    expires_at: int
    created_at: int

class AuthCode(BaseModel):
    code: str
    session_id: str
    expires_at: int
    picture: Optional[str] = None

class Report(BaseModel):
    id: str
    user_id: Optional[str]
    user_email: str
    message: str
    created_at: int
    resolved: bool

# --------------------------------------------------
# Database
# --------------------------------------------------

T = TypeVar("T")
class Database(ABC):
    @abstractmethod
    def query(self, sql: str, params: QueryParams = []) -> list[QueryRow]:
        pass
    
    @abstractmethod
    @contextmanager
    def transaction(self):
        yield
    
    def query_and_map_rows(self, sql: str, map_fn: Callable[[QueryRow], T], params: QueryParams = []) -> list[T]:
        return [map_fn(row) for row in self.query(sql, params)]
    
    E = TypeVar("E", bound=Exception)
    def query_and_map_single(
        self,
        sql: str,
        map_fn: Callable[[dict[str, Any]], T],
        map_index_err: Optional[Callable[[IndexError], E]] = None,
        params: QueryParams = []
    ) -> T:
        try:
            return map_fn(self.query(sql, params)[0])
        except IndexError as index_err:
            raise map_index_err(index_err) if map_index_err else index_err
    
    def try_query_and_map_single(
        self,
        sql: str,
        map_fn: Callable[[dict[str, Any]], T],
        params: QueryParams = []
    ) -> Optional[T]:
        try:
            return self.query_and_map_single(sql, map_fn, None, params)
        except IndexError:
            return None

    #------------------------------
    # Viewing all items in database (including items with quantity 0)
    #------------------------------

    def all_products(self) -> list[Product]:
        return Product.query_and_include_tags(self, "SELECT * FROM products")
    
    def all_product_names(self) -> list[str]:
        return self.query_and_map_rows("SELECT name FROM products", lambda row: str(row["name"]))
    
    def all_product_brands(self) -> list[str]:
        return self.query_and_map_rows("SELECT name FROM brands", lambda row: str(row["name"]))
    
    def all_product_tags(self) -> list[str]:
        return self.query_and_map_rows(
            "SELECT DISTINCT tag_label FROM product_tags pt JOIN products p ON pt.product_id = p.id WHERE p.quantity > 0",
            lambda row: str(row["tag_label"])
        )
    
    #------------------------------
    # Viewing items currently in the pantry (quantity > 0)
    #------------------------------

    def available_products(self) -> list[Product]:
        return Product.query_and_include_tags(self, "SELECT * FROM products WHERE quantity > 0")
    
    def available_product_names(self) -> list[str]:
        return self.query_and_map_rows("SELECT name FROM products WHERE quantity > 0", lambda row: str(row["name"]))
    
    def available_product_brands(self) -> list[str]:
        return self.query_and_map_rows(
            "SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL AND quantity > 0",
            lambda row: str(row["brand"])
        )
    
    def available_product_tags(self) -> list[str]:
        return self.query_and_map_rows(
            "SELECT DISTINCT tag_label FROM product_tags pt JOIN products p ON pt.product_id = p.id WHERE p.quantity > 0",
            lambda row: str(row["tag_label"])
        )
    
    #------------------------------
    # Updating methods
    #------------------------------

    def add_product(
        self,
        id: str,
        name: str,
        brand: Optional[str],
        quantity: Optional[int],
        image_link: Optional[str],
        tags: Optional[list[str]]
    ) -> Product:
        if quantity < 0:
            raise InvalidQuantityError(quantity) 
        with self.transaction():
            fields: list[str] = ["id", "name", "quantity"]
            values: list[str] = ["?", "?", "?"]
            params: QueryParams = [id, name, quantity]
            
            # Insert brand and image link if available
            if brand:
                self.query("INSERT OR IGNORE INTO brands (name) VALUES (?)", [brand])
                fields.append("brand")
                values.append("?")
                params.append(brand)

            if image_link:
                self.query("INSERT OR IGNORE INTO image_links (path) VALUES (?)", [image_link])
                fields.append("image_link")
                values.append("?")
                params.append(image_link)

            self.query(
                    f"INSERT INTO products ({', '.join(fields)}) VALUES ({', '.join(values)})",
                    params
                )

            if tags:
                for tag in tags:
                    self.query("INSERT OR IGNORE INTO tags (label) VALUES (?)", [tag])
                    self.query(
                        "INSERT INTO product_tags (product_id, tag_label) VALUES (?, ?)",
                        [id, tag]
                    )

            return Product(
                id=id,
                name=name,
                brand=brand,
                quantity=quantity if quantity is not None else 0,
                image_link=image_link,
                tags=sorted(tags) if tags else []
            )

    def update_product(
        self,
        id: str,
        name: Union[str, None, Unset] = UNSET,
        brand: Union[str, None, Unset] = UNSET,
        quantity: Union[int, Unset] = UNSET,
        image_link: Union[str, None, Unset] = UNSET,
        tags: Union[list[str], None, Unset] = UNSET,
    ) -> Product:
        with self.transaction():
            fields: list[str] = []
            params: QueryParams = []

            # --- scalar fields ---
            if name is not UNSET:
                fields.append("name = ?")
                params.append(name)

            if brand is not UNSET:
                # Create brand first if it doesn't exist
                if brand is not None:
                    self.query("INSERT OR IGNORE INTO brands (name) VALUES (?)", [brand])
                fields.append("brand = ?")
                params.append(brand)

            if quantity is not UNSET:
                fields.append("quantity = ?")
                params.append(quantity)

            if image_link is not UNSET:
                fields.append("image_link = ?")
                params.append(image_link)

            if fields:
                params.append(id)
                self.query(
                    f"UPDATE products SET {', '.join(fields)} WHERE id = ?",
                    params
                )

            if tags is not UNSET:
                if isinstance(tags, list):
                    # [] = clear, [...] = replace
                    self.query("DELETE FROM product_tags WHERE product_id = ?", [id])

                    for tag in tags:
                        # Create tag first if it doesn't exist
                        self.query("INSERT OR IGNORE INTO tags (label) VALUES (?)", [tag])
                        self.query(
                            "INSERT INTO product_tags (product_id, tag_label) VALUES (?, ?)",
                            [id, tag]
                        )

            return self.product_in_table(id, name if not isinstance(name, type(UNSET)) else "")
    
    def checkout_product(self, id: str, amount: int) -> int:
        """
        Check out a specific quantity of a product given its ID.

        Raises:
            ProductNotFoundError: If no product with the given ID exists.
        """
        with self.transaction():
            # Get old quantity
            old_quantity = self.query_and_map_single(
                "SELECT quantity FROM products WHERE id = ?",
                lambda row: int(row["quantity"]),
                lambda _: ProductNotFoundError(id),
                [id],
            )
            # Calculate new quantity after amount is taken away
            new_quantity = old_quantity - amount
            if new_quantity < 0:
                raise InvalidQuantityError(new_quantity)
            # Update quantity in database
            self.query("UPDATE products SET quantity = ? WHERE id = ?", [new_quantity, id])
            return new_quantity
    
    def add_tags(self, tags: list[str]) -> list[str]:
        """
        Add a list of tags to the database. The tags do not have to be unique.

        Returns:
            The list of tags that were newly added
        """
        with self.transaction():
            existing_tags = self.query_and_map_rows(
                f"SELECT label FROM tags WHERE label IN ({','.join('?' * len(tags))})",
                lambda row: str(row["label"]),
                tags
            )

            # Attempt to add all tags
            for tag in tags:
                self.query("INSERT OR IGNORE INTO tags (label) VALUES (?)", [tag])

            # Return only the newly added tags
            newly_added_tags = [tag for tag in tags if tag not in existing_tags]

            return newly_added_tags

    #-------------------
    #    Save and load
    #------------------

    def save_backup(self) -> None:
        """Saves database to a file"""
        to_write = self.all_products()
        os.makedirs(LOCAL_STATE_DIR, exist_ok=True)
        with open(LOCAL_BACKUP_PRODUCTS_PATH, "w") as f:
            for i in to_write:
                f.write(str(i))
                f.write("\n")
            

    def load_backup(self) -> None:
        """Adds all saved products to main table"""
        self.delete_table()
        with open(LOCAL_BACKUP_PRODUCTS_PATH, "r") as f:
            for line in f:
                new_product = line.strip()
                id = new_product[((new_product.index("id=")) + 4): (new_product.index("name="))].replace("'", "").strip()
                name = new_product[((new_product.index("name=")) + 5): (new_product.index("brand="))].replace("'", "").strip()
                brand = new_product[((new_product.index("brand=")) + 6): (new_product.index("quantity="))].replace("'", "").strip()
                if brand == "None":
                    brand = None
                quantity = new_product[((new_product.index("quantity=")) + 9): (new_product.index("image_link="))].replace("'", "").strip()
                image_link = new_product[((new_product.index("image_link=")) + 11): (new_product.index("tags="))].strip()
                if image_link == "None":
                    image_link = None
                all_tags = new_product[((new_product.index("tags=")) + 6): (len(new_product) - 1)].replace("'", "").strip()
                if all_tags == "None":
                    tags = None
                else:
                    tags = all_tags.split(", ")
                self.add_product(id, name, brand, int(quantity), image_link, tags)

    def delete_table(self) -> None:
        """Only used to load a backup- deletes all products in table"""
        self.query("DELETE FROM products")
    #------------------------------
    # Viewing singles
    #------------------------------


    def product_in_table(self, id: str, name: str, brand: Optional[str] = UNSET) -> Product:
        """
        Checks if a product is in the table

        Raises:
            ProductNotFoundError: If no product with the given ID exists.
        """
        if id: #Search for items with a valid ID
            return self.query_and_map_single("""
                    SELECT p.*, GROUP_CONCAT(pt.tag_label) as tags
                    FROM products p
                    LEFT JOIN product_tags pt ON p.id = pt.product_id
                    WHERE p.id = ?
                    GROUP BY p.id
                """,
                lambda row: Product.from_row(row),
                lambda _: ProductNotFoundError(id),
                [id]
            )
        else:
            if name in self.all_product_names(): #Searches for product by name
                if brand is not UNSET:
                    if brand in self.all_product_brands(): #Searches for brand of product
                        return self.query_and_map_single(
                            f"SELECT p.*, GROUP_CONCAT(pt.tag_label) as tags FROM products p LEFT JOIN product_tags pt ON p.id = pt.product_id WHERE name = ? and brand = ?",
                            lambda row: Product.from_row(row),
                            lambda _: ProductNotFoundError(brand),
                            [name, brand]
                        )
                    else:
                        raise ProductNotFoundError(brand)
                else:
                    return self.query_and_map_single( #No brand available, searches only by name
                        f"SELECT p.*, GROUP_CONCAT(pt.tag_label) as tags FROM products p LEFT JOIN product_tags pt ON p.id = pt.product_id WHERE name = ?",
                        lambda row: Product.from_row(row),
                        lambda _: ProductNotFoundError(name),
                        [name]
                    )
            else:
                raise ProductNotFoundError(name)

    
    def products_search(self, search: str) -> list[Product]:
        like = f"%{search}%"

        sql = """
            SELECT*
            FROM products 
            WHERE 
            name LIKE ?
            OR COALESCE(brand, '') LIKE ?
            OR CAST(id AS TEXT) LIKE ?
            OR id IN (
                SELECT product_id
                FROM product_tags
                WHERE tag_label LIKE ?
                )
            """
        return Product.query_and_include_tags(
            self,
            sql,
            [like, like, like, like]
        )
    
    def products_from_name(self, name: str) -> list[Product]:
        """
        Fetch a list of product by a name. The name can contain the wildcard
        `%` on one or both sides of the name to get general matches, or the 
        wildcard `_` any number of times (`_` acts like `%` but only applies
        to one character). Names are always unique and case insensitive, so 
        without wildcards this function will always return an array containing 
        a single product.

        Returns:
            A list of products with the provided name query (list of one 
            product for an exact name match).
        """
        return Product.query_and_include_tags(self, "SELECT * FROM products WHERE name LIKE ?", [name])
    
    def products_from_brand(self, name: str) -> list[Product]:
        """
        Fetch a list of product by a brand. The brand can contain the wildcard
        `%` on one or both sides of the name to get general matches, or the 
        wildcard `_` any number of times (`_` acts like `%` but only applies
        to one character).

        Returns:
            A list of products with the provided brand query.
        """
        return Product.query_and_include_tags(self, "SELECT * FROM products WHERE brand LIKE ?", [name])
    
    def products_from_matching_tags(self, tags: list[str]) -> list[Product]:
        """
        Fetch a list of product by a list of matching tags. Each tag can contain the wildcard
        `%` on one or both sides to get general matches, or the 
        wildcard `_` any number of times (`_` acts like `%` but only applies
        to one character).

        Returns:
            A list of products with matching tags.
        """
        placeholders = ",".join("?" * len(tags))
        return self.query_and_map_rows(f"""
                SELECT p.*, GROUP_CONCAT(pt2.tag_label) as tags
                FROM products p
                JOIN product_tags pt ON p.id = pt.product_id
                LEFT JOIN product_tags pt2 ON p.id = pt2.product_id
                WHERE pt.tag_label IN ({placeholders})
                GROUP BY p.id
                HAVING COUNT(DISTINCT pt.tag_label) = {len(tags)}
            """,
            lambda row: Product.from_row(row),
            tags
        )
    
    #------------------------------
    # Deleting methods
    #------------------------------

    def remove_product(self, id: int):
        with self.transaction():
            rows = self.query("SELECT id FROM products WHERE id = ?", [id])
            if not rows:
                raise ProductNotFoundError(id)
            
            self.query("DELETE FROM products WHERE id = ?", [id])

    def remove_brand(self, brand: str):
        with self.transaction():
            rows = self.query("SELECT name FROM brands WHERE name = ?", [brand])
            if not rows:
                raise BrandNotFoundError(brand)
            
            self.query("DELETE FROM brands WHERE name = ?", [brand])

    def remove_tag(self, tag: str):
        with self.transaction():
            rows = self.query("SELECT label FROM tags WHERE label = ?", [tag])
            if not rows:
                raise TagNotFoundError(tag)
            
            self.query("DELETE FROM tags WHERE label = ?", [tag])

    #------------------------------
    # Auth
    #------------------------------

    def store_auth_code(self, code: str, session_id: str, picture: Optional[str] = None):
        expires_at = int(time.time()) + 60
        self.query(
            "INSERT INTO auth_codes (code, session_id, expires_at, picture) VALUES (?, ?, ?, ?)",
            [code, session_id, expires_at, picture]
        )
    
    def consume_auth_code(self, code: str) -> Optional[tuple[str, Optional[str]]]:
        with self.transaction():
            auth_code = self.try_query_and_map_single(
                "SELECT * FROM auth_codes WHERE code = ?",
                lambda row: AuthCode(**row),
                [code],
            )
            
            if not auth_code:
                return None
            
            self.query('DELETE FROM auth_codes WHERE code = ?', [code])

            if int(time.time()) > auth_code.expires_at:
                return None
            
            return (auth_code.session_id, auth_code.picture)
        
    MAX_SESSIONS_PER_USER = 5

    def create_auth_session(self, user_id: Optional[str], google_sub: str, refresh_token: str) -> AuthSession:
        session_id = str(uuid.uuid4())
        created_at = int(time.time())
        timeout_days = int(self.get_setting("login_timeout_days") or SESSION_EXPIRY_IN_DAYS)
        expires_at = created_at + 60 * 60 * 24 * timeout_days

        # Lazy cleanup: drop expired sessions for this user on every login
        self.query(
            "DELETE FROM auth_sessions WHERE google_sub = ? AND expires_at <= ?",
            [google_sub, created_at]
        )

        # Enforce session cap: drop oldest sessions beyond (MAX-1) so the new one fits
        existing = self.query(
            "SELECT id FROM auth_sessions WHERE google_sub = ? ORDER BY created_at ASC",
            [google_sub]
        )
        overflow = len(existing) - (self.MAX_SESSIONS_PER_USER - 1)
        if overflow > 0:
            ids_to_drop = [row["id"] for row in existing[:overflow]]
            placeholders = ",".join("?" * len(ids_to_drop))
            self.query(f"DELETE FROM auth_sessions WHERE id IN ({placeholders})", ids_to_drop)

        self.query(
            "INSERT INTO auth_sessions (id, user_id, google_sub, refresh_token, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
            [session_id, user_id, google_sub, refresh_token, created_at, expires_at]
        )

        # Backfill any old visitor sessions (user_id=NULL) for this google_sub
        if user_id:
            self.query(
                "UPDATE auth_sessions SET user_id = ? WHERE google_sub = ? AND user_id IS NULL",
                [user_id, google_sub]
            )

        return AuthSession(id=session_id, user_id=user_id, google_sub=google_sub, refresh_token=refresh_token, created_at=created_at, expires_at=expires_at)

    def purge_expired_sessions(self):
        self.query("DELETE FROM auth_sessions WHERE expires_at <= ?", [int(time.time())])
    
    def get_auth_session(self, session_id: str) -> Optional[AuthSession]:
        session = self.try_query_and_map_single(
            "SELECT * FROM auth_sessions WHERE id = ?",
            lambda row: AuthSession(**row),
            [session_id]
        )

        if not session:
            return None

        # is this session expired?
        if session.expires_at and int(time.time()) > session.expires_at:
            self.query("DELETE FROM auth_sessions WHERE id = ?", [session_id])
            return None
        
        return session

    def get_user(self, id: str) -> Optional[User]:
        return self.try_query_and_map_single(
            "SELECT * FROM users WHERE id = ?",
            lambda row: User(**row),
            [id]
        )

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.try_query_and_map_single(
            "SELECT * FROM users WHERE email = ?",
            lambda row: User(**row),
            [normalize_email(email)]
        )

    def all_users(self) -> list[User]:
        return self.query_and_map_rows("SELECT * FROM users", lambda row: User(**row))

    def count_admin_users(self) -> int:
        return int(self.query(
            "SELECT COUNT(*) as total FROM users WHERE access_level = ?",
            [str(AccessLevel.ADMIN)]
        )[0]["total"])

    def get_setting(self, key: str) -> Optional[str]:
        row = self.try_query_and_map_single(
            "SELECT value FROM settings WHERE key = ?",
            lambda r: str(r["value"]),
            [key]
        )
        return row

    def get_all_settings(self) -> dict[str, str]:
        rows = self.query("SELECT key, value FROM settings")
        return {str(r["key"]): str(r["value"]) for r in rows}

    def update_setting(self, key: str, value: str):
        self.query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", [key, value])
    
    def add_user(self, email: str, access_level: AccessLevel, id: Optional[str] = None):
        normalized_email = normalize_email(email)
        user_id = id or str(uuid.uuid4())

        with self.transaction():
            if self.get_user_by_email(normalized_email):
                raise UserAlreadyExistsError(normalized_email)

            try:
                self.query(
                    "INSERT INTO users (id, email, access_level) VALUES (?, ?, ?)",
                    [user_id, normalized_email, access_level]
                )
                # update any existing visitor sessions for this user
                if id:
                    self.query(
                        "UPDATE auth_sessions SET user_id = ? WHERE google_sub = ? AND user_id IS NULL",
                        [user_id, id]
                    )
                return User(id=user_id, email=normalized_email, access_level=access_level)
            except sqlite3.IntegrityError:
                raise UserAlreadyExistsError(normalized_email)

    def set_user_picture(self, id: str, picture: Optional[str]):
        self.query("UPDATE users SET picture = ? WHERE id = ?", [picture, id])

    def update_user_access_level(self, id: str, access_level: AccessLevel, acting_user_id: Optional[str] = None) -> User:
        user = self.get_user(id)
        if not user:
            raise UserNotFoundError(id)

        if (
            acting_user_id == user.id
            and user.access_level == AccessLevel.ADMIN
            # and access_level.value == AccessLevel.ADMIN
            and self.count_admin_users() <= 1
        ):
            raise CannotDemoteOnlyAdminError()

        self.query("UPDATE users SET access_level = ? WHERE id = ?", [access_level.value, id])
        user = self.get_user(id)
        if not user:
            raise UserNotFoundError(id)
        return user

    def add_report(self, user_id: Optional[str], user_email: str, message: str) -> Report:
        report_id = str(uuid.uuid4())
        created_at = int(time.time())
        self.query(
            "INSERT INTO reports (id, user_id, user_email, message, created_at, resolved) VALUES (?, ?, ?, ?, ?, 0)",
            [report_id, user_id, user_email, message, created_at]
        )
        return Report(
            id=report_id,
            user_id=user_id,
            user_email=user_email,
            message=message,
            created_at=created_at,
            resolved=False
        )

    def get_reports(self) -> list[Report]:
        return self.query_and_map_rows(
            "SELECT * FROM reports ORDER BY created_at DESC",
            lambda row: Report(**row)
        )

    def resolve_report(self, report_id: str):
        self.query("UPDATE reports SET resolved = 1 WHERE id = ?", [report_id])

    def all_sessions(self) -> list[AuthSession]:
        return self.query_and_map_rows("SELECT * FROM auth_sessions", lambda row: AuthSession(**row))

    def revoke_session(self, session_id: str):
        self.query("DELETE FROM auth_sessions WHERE id = ?", [session_id])

def connect(locally: bool) -> Database:
    if locally:
        return LocalDatabase()
    return RemoteDatabase()

class RemoteQueryError(Exception):
    def __init__(self, data: Any):
        errors = data.get('errors') or data.get('body') or data
        super().__init__(f"D1 query failed: {errors}")

class RemoteDatabase(Database):
    def __init__(self):
        account_id = env_get("CLOUDFLARE_ACCOUNT_ID")
        db_id = env_get("CLOUDFLARE_D1_DATABASE_ID")
        d1_api_token = env_get("CLOUDFLARE_D1_API_TOKEN")

        self.query_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{db_id}/query"
        self.headers = {
            "Authorization": f"Bearer {d1_api_token}",
            "Content-Type": "application/json"
        }

    def query(self, sql: str, params: QueryParams = []) -> list[Any]:
        body: dict[str, Any] = {"sql": sql}
        if params:
            body["params"] = params

        response = requests.post(self.query_url, headers=self.headers, json=body)
        if not response.ok:
            raise RemoteQueryError({"status": response.status_code, "body": response.text, "sql": sql})
        data = response.json()

        if not data.get("success"):
            raise RemoteQueryError(data)

        results = data.get("result", [])
        if not results:
            return []

        return results[0].get("results", [])
    
    @contextmanager
    def transaction(self):
        # D1 REST API doesn't support explicit transaction management via SQL
        # (BEGIN/COMMIT/ROLLBACK). Each HTTP request is an isolated connection.
        # Operations run in autocommit mode.
        yield
    
class LocalDatabase(Database):
    LOCAL_DATABASE_PATH = os.path.join(os.path.dirname(__file__), "__local__", "local_db.sqlite3")
    MIGRATIONS_PATH = os.path.join(os.path.dirname(__file__), "migrations")

    def __init__(self):
        os.makedirs(os.path.dirname(self.LOCAL_DATABASE_PATH), exist_ok=True)
        self.conn = sqlite3.connect(self.LOCAL_DATABASE_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._run_migrations()

    def _run_migrations(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS migrations (
                filename TEXT PRIMARY KEY,
                applied_at INTEGER NOT NULL
            )
        """)

        migration_files = sorted(os.listdir(self.MIGRATIONS_PATH))
        for filename in migration_files:
            if not filename.endswith(".sql"):
                continue

            already_applied = self.conn.execute(
                "SELECT 1 FROM migrations WHERE filename = ?", (filename,)
            ).fetchone()

            if already_applied:
                continue

            path = os.path.join(self.MIGRATIONS_PATH, filename)
            with open(path, "r") as f:
                self.conn.executescript(f.read())

            self.conn.execute(
                "INSERT INTO migrations (filename, applied_at) VALUES (?, ?)",
                (filename, int(time.time()))
            )
            self.conn.commit()
            print(f"Applied migration: {filename}")

    def query(self, sql: str, params: QueryParams = []) -> list[Any]:
        cursor = self.conn.execute(sql, params)
        self.conn.commit()
        return [dict(row) for row in cursor.fetchall()]
    
    @contextmanager
    def transaction(self):
        with self.conn:
            yield

def normalize_email(email: str) -> str:
    return email.strip().lower()
