import sys
from pathlib import Path

import pytest

# Add the repository root to sys.path so tests can import the backend package.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

#to run: python -m pytest tests/test_database.py

import backend.database as database
from backend.database import (
    LocalDatabase,
    InvalidQuantityError,
    ProductNotFoundError,
    UserAlreadyExistsError,
    AccessLevel,
    BrandNotFoundError,
    TagNotFoundError
)


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = tmp_path / "local_db.sqlite3"
    monkeypatch.setattr(database.LocalDatabase, "LOCAL_DATABASE_PATH", str(db_path))
    return database.LocalDatabase()

def test_remove_product(db):
    product = db.add_product(str("121212"), "Test Cereal", "mybrand", 2, None, ["tag_1", "tag_2", "tag_3"])
    product = db.add_product(str("1212"), "Test Cereal", "mybrand", 2, None, ["tag_1", "tag_2"])

    brands = db.all_product_brands()
    assert brands == ['mybrand']
    tags = db.all_product_tags()
    assert tags == ['tag_1', 'tag_2', 'tag_3']

    db.remove_product("121212")
    brands = db.all_product_brands()
    assert brands == ['mybrand']
    tags = db.all_product_tags()
    assert tags == ['tag_1', 'tag_2']
    db.remove_product("1212")
    brands = db.all_product_brands()
    assert brands == []
    tags = db.all_product_tags()
    assert tags == []

    product = db.add_product(str("122122"), "Test Cereal", None, 2, None, [])
    brands = db.all_product_brands()
    assert brands == []
    tags = db.all_product_tags()
    assert tags == []
    db.remove_product("122122")
    brands = db.all_product_brands()
    assert brands == []
    tags = db.all_product_tags()
    assert tags == []


def test_query_and_map_rows(db):
    db.query("INSERT INTO brands (name) VALUES (?)", ["Test Brand"])
    brands = db.query_and_map_rows("SELECT name FROM brands", lambda row: row["name"])
    print(len(brands))
    
    #assert 1 == 2
    print(len(brands))
    assert brands == ["Test Brand"] #Ensure brand is in table
    db.remove_brand("Test Brand")
    brands = db.query_and_map_rows("SELECT name FROM brands", lambda row: row["name"])
    assert brands == [] #Ensure brand is removed


def test_add_product_and_product_in_table(db):
    product = db.add_product(str("121212"), "Test Cereal", None, 2, None, ["tag_1", "tag_2"])

    assert product.name == "Test Cereal"
    assert product.brand == None
    assert set(product.tags) == {"tag_1", "tag_2"}

    loaded = db.product_in_table(product.id, product.name, product.brand)
    assert loaded == product #Ensures product is in the table
    assert product.id == str("121212")
    db.remove_product(product.id) 
    with pytest.raises(ProductNotFoundError):
        db.product_in_table(product.id, product.name, product.brand) #Ensures product is removed

def test_in_table(db):
    product1 = db.add_product(str("333333333"), "fdsadasfd", "brand!!!", 2, None, ["fdsafas", "ffff"])
    with pytest.raises(ProductNotFoundError):
        db.product_in_table("", "notintable", product1.brand)
    db.product_in_table("", product1.name, product1.brand)
    db.product_in_table("", product1.name)
    with pytest.raises(ProductNotFoundError):
        db.product_in_table("", product1.name, "notintable")
    product2 = db.add_product(str("29292929"), "aaaaaa", "brand!!!", 2, None, ["fdsafas", "ffff"])
    product3 = db.add_product(str("22393923"), "fdsadasfd", "brand!!", 2, None, ["fdsafas", "ffff"])
    assert product2 == db.product_in_table("", product2.name, product2.brand)
    assert product3 == db.product_in_table("", product3.name, product3.brand)


def test_save_and_load(db):
    product1 = db.add_product(str("333333333"), "fdsadasfd", "brand!!!", 2, None, ["fdsafas", "ffff"])
    product2 = db.add_product(str("2423423"), "aaaaaaaaaaaaaaaa", "new brand", 2, None, [])
    product3 = db.add_product(str("44444444444"), "dsafds", None, 0, None, ["green", "blue"])
    product4 = db.add_product(str("02920202"), "llllllllll", None, 211, None, ["grilled cheese", "hello", "3323233"])
    product5 = db.add_product(str("112"), "Test Cereal", None, 2, None, ["tag_1", "tag_2"])

    db.save_backup()
    #Removing products
    db.remove_product(product1.id) 
    with pytest.raises(ProductNotFoundError):
        db.product_in_table(product1.id, product1.name, product1.brand) 
    db.remove_product(product2.id) 
    with pytest.raises(ProductNotFoundError):
        db.product_in_table(product2.id, product2.name, product2.brand) 
    
    #Adding product that won't be saved
    product6 = db.add_product(str("430232"), "fdsadasfd", None, 2010, "linafdsaflkw/dslafjdkls", ["dflsafd", "25oi23o", "fdsafda", "Ffff"])
    assert db.product_in_table(product6.id, product6.name, product6.brand) == product6

    db.load_backup()

    assert db.product_in_table(product1.id, product1.name, product1.brand) == product1
    assert db.product_in_table(product2.id, product2.name, product2.brand) == product2
    assert db.product_in_table(product3.id, product3.name, product3.brand) == product3
    assert db.product_in_table(product4.id, product4.name, product4.brand) == product4
    assert db.product_in_table(product5.id, product5.name, product5.brand) == product5
    with pytest.raises(ProductNotFoundError):
        db.product_in_table(product6.id, product6.name, product6.brand) #Ensures product isn't in database



def test_remove_product_raises_when_not_found(db):
    with pytest.raises(ProductNotFoundError):
        db.remove_product("99900999")


def test_invalid_quantity_for_add_and_checkout(db):
    with pytest.raises(InvalidQuantityError):
        db.add_product("4242342", "Bad Item", "Brand", -1, None, [])

    product = db.add_product("35435354", "Checkout Item", "Brand", 1, None, [])
    with pytest.raises(InvalidQuantityError):
        db.checkout_product(product.id, 2)


def test_update_product_clears_tags(db):
    product = db.add_product("676767", "Update Item", "Brand", 5, None, ["old_tag"])
    updated = db.update_product(product.id, tags=[])

    assert updated.tags == []
    tags = db.product_in_table(product.id, product.name, product.brand)
    assert tags.id == product.id
    assert tags.tags == []
    db.remove_product(product.id)
    with pytest.raises(ProductNotFoundError):
        db.product_in_table(product.id, product.name, product.brand)


def test_add_user_duplicate_email_raises(db):
    user = db.add_user("USER@Example.com", AccessLevel.TRUSTED)
    assert user.email == "user@example.com"

    with pytest.raises(UserAlreadyExistsError):
        db.add_user("user@example.com", AccessLevel.TRUSTED)


def test_checkout(db):
    product = db.add_product("234234", "Green Beans", None, 50, None, ['tag_!', 'tag_?'])
    assert product.name == "Green Beans"
    assert product.brand == None
    assert set(product.tags) == {"tag_!", "tag_?"}

    loaded = db.product_in_table(product.id, product.name, product.brand)
    assert loaded == product #Ensures product is in the table

    db.checkout_product(product.id, 3) #Ensures quantity is updated
    updated_product = db.product_in_table(product.id, product.name, product.brand)
    assert updated_product.quantity == 47
    db.checkout_product(product.id, 47)
    updated_product = db.product_in_table(product.id, product.name, product.brand)
    assert updated_product.quantity == 0
    
    db.update_product(product.id, quantity= 4) #Ensures all parts of the product are maintained
    updated_product = db.product_in_table(product.id, product.name, product.brand)
    assert updated_product.quantity == 4
    assert updated_product.name == "Green Beans"
    assert updated_product.brand == None
    assert set(updated_product.tags) == {"tag_!", "tag_?"}
    
    with pytest.raises(InvalidQuantityError): #Ensures invalid quantity can't be checkedout
        db.checkout_product(product.id, 47)
    updated_product = db.product_in_table(product.id, product.name, product.brand)
    assert updated_product.quantity == 4
    
    db.remove_product(product.id) 
    with pytest.raises(ProductNotFoundError):
        db.product_in_table(product.id, product.name, product.brand) #Ensures product is removed
        
    