import dotenv
from flask.testing import FlaskClient
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import database
from database import Database, Product
import api
from misc import env_get

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "local.env")
dotenv.load_dotenv(env_path)

DEV_TOKEN = env_get("DEV_TOKEN")


@pytest.fixture(scope="session", autouse=True)
def wipe_database():
    test_db = database.connect(True)
    test_db.query("DELETE FROM product_tags")
    test_db.query("DELETE FROM products")
    test_db.query("DELETE FROM brands")
    test_db.query("DELETE FROM tags")
    test_db.query("DELETE FROM image_links")
    test_db.query("DELETE FROM auth_sessions")
    test_db.query("DELETE FROM users")
    
@pytest.fixture
def db():
    db = database.connect(True)
    yield db

@pytest.fixture
def client(db: Database):
    app = api.create_app(db, is_local=True)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_all_products(client: FlaskClient):
    response = client.get("/products/all", headers={"Authorization": DEV_TOKEN})
    assert response.status_code == 200
    assert isinstance(response.json, list)

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

    # # test updating
    # response = client.post("/products", json=[{
    #     "id": str(product.id),
    #     "tags": product.tags
    # }], headers={"Authorization": DEV_TOKEN})

    # assert response.status_code == 201
    # response_json = response.json
    # assert response_json
    # added_products = [Product.model_validate(product_json) for product_json in response_json["added"]]
    # product = added_products[0]
