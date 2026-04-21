import pytest
from contextlib import nullcontext
from unittest.mock import MagicMock

from backend.database import Database, Product, Tag, ProductNotFoundError, NotEnoughProductStockError, AccessLevel

DEV_TOKEN = 'test-dev-token'

REQUIRED_ENV = {
    'DEV_TOKEN': DEV_TOKEN,
    'FLASK_SECRET_KEY': 'test-secret',
    'VITE_API_PORT': '5000',
    'VITE_API_URL': 'http://localhost',
    'WEBSITE_URL': 'http://localhost',
    'VITE_GOOGLE_CLIENT_ID': 'test-client-id',
    'GOOGLE_CLIENT_SECRET': 'test-secret',
}


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def db():
    mock = MagicMock(spec=Database)
    mock.transaction.return_value = nullcontext()
    # Default returns for methods that need real data
    mock.query_and_map_rows.return_value = []
    mock.query.return_value = []
    mock.all_product_names.return_value = []
    mock.all_product_brands.return_value = []
    mock.all_product_tags.return_value = []
    mock.available_products.return_value = []
    mock.available_product_names.return_value = []
    mock.available_product_brands.return_value = []
    mock.available_product_tags.return_value = []
    return mock


@pytest.fixture
def app(db, env_setup):
    from backend.api import create_app
    flask_app = create_app(db, is_local=True)
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def auth():
    return {'Authorization': DEV_TOKEN}


@pytest.fixture
def products():
    return [
        Product(id='3835982', name='corn',           brand='HEB',           quantity=4,  image_link=None, tags=['VEGETABLES', 'canned']),
        Product(id='95827',   name='corn',           brand='green giant',   quantity=14, image_link=None, tags=['VEGETABLES', 'canned']),
        Product(id='4329',    name='tomato paste',   brand='HEB',           quantity=17, image_link=None, tags=['VEGETABLES']),
        Product(id='324',     name='peas',           brand='green giant',   quantity=2,  image_link=None, tags=['VEGETABLES', 'canned']),
        Product(id='48328',   name='cherrios',       brand='general mills', quantity=8,  image_link=None, tags=['cereal']),
        Product(id='1288901', name='pasta',          brand='walmart',       quantity=6,  image_link=None, tags=['pasta', 'nut free']),
        Product(id='68234',   name='roasted tomatoes', brand='HEB',         quantity=0,  image_link=None, tags=['VEGETABLES']),
        Product(id='1117362', name='oatmeal',        brand='HEB',           quantity=0,  image_link=None, tags=[]),
    ]


@pytest.fixture
def inventory(products):
    return [p for p in products if p.quantity > 0]


@pytest.fixture
def tag_list():
    return [Tag(label=t) for t in ['VEGETABLES', 'canned', 'cereal', 'pasta', 'nut free']]
