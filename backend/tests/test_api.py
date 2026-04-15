import dotenv
from flask.testing import FlaskClient
import pytest
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import database
from database import AccessLevel, Database, Product
import api
from misc import env_get

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "local.env")
dotenv.load_dotenv(env_path)

DEV_TOKEN = env_get("DEV_TOKEN")

@pytest.fixture(scope="session", autouse=True)
def isolated_test_database(tmp_path_factory: pytest.TempPathFactory):
    temp_dir = tmp_path_factory.mktemp("ppit-test-db")
    db_path = temp_dir / "test_db.sqlite3"
    original_path = database.LocalDatabase.LOCAL_DATABASE_PATH
    database.LocalDatabase.LOCAL_DATABASE_PATH = str(db_path)

    try:
        yield
    finally:
        database.LocalDatabase.LOCAL_DATABASE_PATH = original_path
        for suffix in ("", "-wal", "-shm"):
            file_path = Path(f"{db_path}{suffix}")
            if file_path.exists():
                file_path.unlink()
    
@pytest.fixture
def db():
    db = database.connect(True)
    yield db
    if isinstance(db, database.LocalDatabase):
        db.conn.close()

@pytest.fixture
def client(db: Database):
    app = api.create_app(db, is_local=True)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_all_products(client: FlaskClient):
    response = client.get("/products", headers={"Authorization": DEV_TOKEN})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert "data" in response.json # pyright: ignore[reportUnknownMemberType]
    assert "total" in response.json # pyright: ignore[reportUnknownMemberType]
    assert "total_pages" in response.json # pyright: ignore[reportUnknownMemberType]
    assert isinstance(response.json["data"], list) # pyright: ignore[reportUnknownMemberType]

def test_add_product(client: FlaskClient):
    # test adding a new product
    response = client.post("/products", json=[{
        "name": "Test Product",
        "brand": "Test Brand",
        "quantity": 10,
        "image_link": None,
        "tags": ["tag1", "tag2"]
    }], headers={"Authorization": DEV_TOKEN})

    assert response.status_code == 201
    response_json = response.json
    assert response_json
    added_products = [Product.model_validate(product_json) for product_json in response_json["added"]]
    product = added_products[0]

    assert product.name == "Test Product"
    assert product.brand == "Test Brand"
    assert product.quantity == 10
    assert len(product.tags) == 2

def test_update_product(client: FlaskClient):
    response = client.post("/products", json=[{
        "name": "Test Product",
        "brand": "Test Brand",
        "quantity": 10,
        "image_link": None,
        "tags": ["tag1", "tag2"]
    }], headers={"Authorization": DEV_TOKEN})
    assert response.status_code == 201
    response_json = response.json
    assert response_json
    added_products = [Product.model_validate(product_json) for product_json in response_json["added"]]
    product = added_products[0]

    update_response = client.post("/products", json=[{
        "id": product.id,
        "name": "Updated Test Product",
        "quantity": 6,
        "tags": ["tag2"],
    }], headers={"Authorization": DEV_TOKEN})

    assert update_response.status_code == 201
    update_json = update_response.json
    assert update_json
    updated_products = [Product.model_validate(product_json) for product_json in update_json["added"]]
    updated = updated_products[0]

    assert updated.id == product.id
    assert updated.name == "Updated Test Product"
    assert updated.brand == "Test Brand"  # unchanged field
    assert updated.quantity == 6
    assert set(updated.tags) == {"tag2"}

def test_add_user_only_requires_email(client: FlaskClient):
    response = client.post(
        "/user",
        query_string={
            "email": "new_user@Southwestern.edu",
            "access_level": "trusted",
        },
        headers={"Authorization": DEV_TOKEN},
    )

    assert response.status_code == 201
    assert response.json
    assert response.json["email"] == "new_user@southwestern.edu"
    assert response.json["access_level"] == "trusted"
    assert response.json["id"]

class MockGoogleTokenResponse:
    def __init__(self, payload: dict[str, str]):
        self.payload = payload

    def json(self) -> dict[str, str]:
        return self.payload

def test_google_callback_authorizes_user_by_email(client: FlaskClient, db: Database, monkeypatch: pytest.MonkeyPatch):
    db.add_user("authorized_user@southwestern.edu", AccessLevel.TRUSTED)

    def mock_post(*args, **kwargs): # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
        return MockGoogleTokenResponse({
            "id_token": "fake-id-token",
            "refresh_token": "fake-refresh-token",
        })

    def mock_decode(*args, **kwargs): # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
        return {
            "email": "authorized_user@southwestern.edu",
            "sub": "google-sub-123",
            "picture": "https://example.com/picture.png",
        }

    monkeypatch.setattr(api.requests, "post", mock_post) # pyright: ignore[reportUnknownArgumentType]
    monkeypatch.setattr(api.jwt, "decode", mock_decode) # pyright: ignore[reportUnknownArgumentType]

    response = client.get("/auth/google/callback?code=fake-code")

    assert response.status_code == 302
    assert response.location
    auth_code = response.location.split("code=")[-1]

    exchange = client.post("/auth/exchange", json={"code": auth_code})
    assert exchange.status_code == 200
    assert exchange.json
    session_id = exchange.json["session"]

    user_response = client.get("/user", headers={"Authorization": session_id})
    assert user_response.status_code == 200
    assert user_response.json
    assert user_response.json["email"] == "authorized_user@southwestern.edu"
    assert user_response.json["access_level"] == "trusted"

def test_only_admin_cannot_revoke_own_admin_privileges(client: FlaskClient, db: Database):
    sole_admin = db.add_user("sole_admin@southwestern.edu", AccessLevel.ADMIN)
    session = db.create_auth_session(sole_admin.id, "sole-admin-sub", "refresh-token")

    response = client.patch(
        f"/user/{sole_admin.id}",
        json={"access_level": "trusted"},
        headers={"Authorization": session.id},
    )

    assert response.status_code == 400
    assert response.json
    assert "only admin" in response.json["error"].lower()
    assert db.get_user(sole_admin.id)
    assert db.get_user(sole_admin.id).access_level == AccessLevel.ADMIN # pyright: ignore[reportOptionalMemberAccess]
