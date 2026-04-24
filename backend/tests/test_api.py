import pytest
from unittest.mock import MagicMock
from backend.database import Product, Tag, ProductNotFoundError, AccessLevel


# ==================================================
# GET /products
# ==================================================

def test_get_products_empty(auth, client, db):
    db.query.return_value = [{'total': 0}]
    db.query_and_map_rows.return_value = []
    res = client.get('/products', headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert data['data'] == []
    assert data['total'] == 0


def test_get_products(auth, client, db, products):
    db.query.return_value = [{'total': len(products)}]
    db.query_and_map_rows.return_value = products
    res = client.get('/products', headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['data']) == len(products)
    assert data['total'] == len(products)


def test_get_products_no_auth(client):
    res = client.get('/products')
    assert res.status_code == 401


def test_get_products_by_name(auth, client, db, products):
    corn = [p for p in products if p.name == 'corn']
    db.query.return_value = [{'total': len(corn)}]
    db.query_and_map_rows.return_value = corn
    res = client.get('/products?name=corn', headers=auth)
    assert res.status_code == 200


def test_get_products_by_id(auth, client, db, products):
    match = [p for p in products if p.id == '3835982']
    db.query.return_value = [{'total': len(match)}]
    db.query_and_map_rows.return_value = match
    res = client.get('/products?id=3835982', headers=auth)
    assert res.status_code == 200
    assert len(res.get_json()['data']) == 1


def test_get_products_by_brand(auth, client, db, products):
    match = [p for p in products if p.brand == 'HEB']
    db.query.return_value = [{'total': len(match)}]
    db.query_and_map_rows.return_value = match
    res = client.get('/products?brand=HEB', headers=auth)
    assert res.status_code == 200


def test_get_products_by_exact_quantity(auth, client, db, products):
    match = [p for p in products if p.quantity == 4]
    db.query.return_value = [{'total': len(match)}]
    db.query_and_map_rows.return_value = match
    res = client.get('/products?quantity=4', headers=auth)
    assert res.status_code == 200


def test_get_products_by_quantity_range(auth, client, db, products):
    match = [p for p in products if 3 <= p.quantity <= 10]
    db.query.return_value = [{'total': len(match)}]
    db.query_and_map_rows.return_value = match
    res = client.get('/products?quantity=3:10', headers=auth)
    assert res.status_code == 200


def test_get_products_by_quantity_lower_bound(auth, client, db, products):
    match = [p for p in products if p.quantity >= 5]
    db.query.return_value = [{'total': len(match)}]
    db.query_and_map_rows.return_value = match
    res = client.get('/products?quantity=5:', headers=auth)
    assert res.status_code == 200


def test_get_products_by_quantity_upper_bound(auth, client, db, products):
    match = [p for p in products if p.quantity <= 10]
    db.query.return_value = [{'total': len(match)}]
    db.query_and_map_rows.return_value = match
    res = client.get('/products?quantity=:10', headers=auth)
    assert res.status_code == 200


def test_get_products_invalid_quantity(auth, client):
    res = client.get('/products?quantity=ten', headers=auth)
    assert res.status_code == 400



def test_get_products_invalid_range_quantity(auth, client):
    res = client.get('/products?quantity=5:seven', headers=auth)
    assert res.status_code == 400


def test_get_products_empty_range_quantity(auth, client):
    res = client.get('/products?quantity=:', headers=auth)
    assert res.status_code == 400


def test_get_products_by_tags(auth, client, db, products):
    match = [p for p in products if 'VEGETABLES' in p.tags]
    db.query.return_value = [{'total': len(match)}]
    db.query_and_map_rows.return_value = match
    res = client.get('/products?tags=VEGETABLES', headers=auth)
    assert res.status_code == 200


def test_get_products_paginated(auth, client, db, products):
    db.query.return_value = [{'total': len(products)}]
    db.query_and_map_rows.return_value = products[:2]
    res = client.get('/products?page=1&page_size=2', headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['data']) == 2
    assert data['total'] == len(products)


# ==================================================
# POST /products
# ==================================================

def test_post_products_new(auth, client, db):
    new_product = Product(id='999', name='olives', brand='everyday olives', quantity=5, image_link=None, tags=[])
    db.product_in_table.side_effect = ProductNotFoundError('999')
    db.add_product.return_value = new_product
    res = client.post('/products', json=[{'id': '999', 'name': 'olives', 'brand': 'everyday olives', 'quantity': 5}], headers=auth)
    assert res.status_code == 201
    data = res.get_json()
    assert data['errors'] == []
    assert len(data['added']) == 1
    assert data['added'][0]['name'] == 'olives'


def test_post_products_update(auth, client, db, products):
    existing = products[3]  # peas
    updated = Product(id=existing.id, name='sweet peas', brand=existing.brand, quantity=5, image_link=None, tags=['VEGETABLES', 'canned'])
    db.product_in_table.return_value = existing
    db.update_product.return_value = updated
    res = client.post('/products', json=[{'id': existing.id, 'name': 'sweet peas', 'quantity': 5}], headers=auth)
    assert res.status_code == 201
    data = res.get_json()
    assert len(data['added']) == 1
    assert data['added'][0]['name'] == 'sweet peas'


def test_post_products_not_a_list(auth, client):
    res = client.post('/products', json={'name': 'olives'}, headers=auth)
    assert res.status_code == 400
    assert res.get_json()['error'] == 'Expected a list of products'


def test_post_product_no_name_new(auth, client, db):
    db.product_in_table.side_effect = ProductNotFoundError('1288901')
    res = client.post('/products', json=[{'brand': 'walmart', 'id': '1288901', 'quantity': 6}], headers=auth)
    assert res.status_code == 207
    data = res.get_json()
    assert len(data['errors']) == 1
    assert data['errors'][0]['error'] == 'Name is required for new products'


def test_post_products_invalid_name_asterisk(auth, client, db):
    db.product_in_table.side_effect = ProductNotFoundError('123')
    res = client.post('/products', json=[{'name': 'pas*ta', 'id': '123', 'quantity': 6}], headers=auth)
    data = res.get_json()
    assert len(data['errors']) > 0


def test_post_products_invalid_name_double_spaces(auth, client, db):
    db.product_in_table.side_effect = ProductNotFoundError('123')
    res = client.post('/products', json=[{'name': 'pas  ta', 'id': '123', 'quantity': 6}], headers=auth)
    data = res.get_json()
    assert len(data['errors']) > 0


def test_post_products_invalid_name_whitespace_only(auth, client, db):
    db.product_in_table.side_effect = ProductNotFoundError('123')
    res = client.post('/products', json=[{'name': '   ', 'id': '123', 'quantity': 6}], headers=auth)
    data = res.get_json()
    assert len(data['errors']) > 0


def test_post_products_invalid_tag(auth, client, db):
    db.product_in_table.side_effect = ProductNotFoundError('123')
    res = client.post('/products', json=[{'name': 'pasta', 'id': '123', 'quantity': 6, 'tags': ['pas!!!!@ta']}], headers=auth)
    data = res.get_json()
    assert len(data['errors']) > 0


def test_post_products_quantity_type_error(auth, client, db):
    db.product_in_table.side_effect = ProductNotFoundError('123')
    res = client.post('/products', json=[{'name': 'pasta', 'id': '123', 'quantity': 'six'}], headers=auth)
    assert len(res.get_json()['errors']) > 0




# ==================================================
# DELETE /products
# ==================================================

def test_delete_products_single(auth, client, db):
    db.query.return_value = []
    res = client.delete('/products', json={'ids': ['3835982']}, headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert '3835982' in data['deleted']
    assert data['errors'] == []


def test_delete_products_multiple(auth, client, db):
    db.query.return_value = []
    ids = ['95827', '324', '48328']
    res = client.delete('/products', json={'ids': ids}, headers=auth)
    assert res.status_code == 200
    assert set(res.get_json()['deleted']) == set(ids)


def test_delete_products_empty_list(auth, client):
    res = client.delete('/products', json={'ids': []}, headers=auth)
    assert res.status_code == 200
    assert res.get_json()['deleted'] == []




def test_delete_products_db_error_returns_207(auth, client, db):
    db.query.side_effect = Exception('DB error')
    res = client.delete('/products', json={'ids': ['000000']}, headers=auth)
    assert res.status_code == 207
    assert len(res.get_json()['errors']) == 1


# ==================================================
# GET /tags
# ==================================================

def test_get_tags_all(auth, client, db, tag_list):
    db.query_and_map_rows.return_value = tag_list
    db.query.return_value = [{'total': len(tag_list)}]
    res = client.get('/tags', headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert data['total'] == len(tag_list)
    assert len(data['data']) == len(tag_list)


def test_get_tags_empty(auth, client, db):
    db.query_and_map_rows.return_value = []
    db.query.return_value = [{'total': 0}]
    res = client.get('/tags', headers=auth)
    assert res.status_code == 200
    assert res.get_json()['data'] == []


def test_get_tags_filtered(auth, client, db):
    canned = [Tag(label='canned')]
    db.query_and_map_rows.return_value = canned
    db.query.return_value = [{'total': 1}]
    res = client.get('/tags?label=canned', headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert all(t['label'] == 'canned' for t in data['data'])


def test_get_tags_nonexistent(auth, client, db):
    db.query_and_map_rows.return_value = []
    db.query.return_value = [{'total': 0}]
    res = client.get('/tags?label=nonexistent', headers=auth)
    assert res.status_code == 200
    assert res.get_json()['data'] == []


# ==================================================
# POST /tags
# ==================================================

def test_post_tags_single(auth, client, db):
    db.query.return_value = []
    res = client.post('/tags', json={'labels': ['vegan']}, headers=auth)
    assert res.status_code == 201
    assert 'vegan' in res.get_json()['added']


def test_post_tags_multiple(auth, client, db):
    db.query.return_value = []
    new_labels = ['toiletries', 'soap', 'gluten free']
    res = client.post('/tags', json={'labels': new_labels}, headers=auth)
    assert res.status_code == 201
    assert set(res.get_json()['added']) == set(new_labels)


def test_post_tags_empty_list(auth, client):
    res = client.post('/tags', json={'labels': []}, headers=auth)
    assert res.status_code == 201
    assert res.get_json()['added'] == []


def test_post_tags_missing_labels_field(auth, client):
    res = client.post('/tags', json={'wrong': []}, headers=auth)
    assert res.status_code == 400


def test_post_tags_invalid_label_double_spaces(auth, client):
    res = client.post('/tags', json={'labels': ['dairy  free']}, headers=auth)
    assert res.status_code == 400




def test_post_tags_db_error_returns_207(auth, client, db):
    db.query.side_effect = Exception('DB failure')
    res = client.post('/tags', json={'labels': ['vegan']}, headers=auth)
    assert res.status_code == 207
    assert len(res.get_json()['errors']) == 1


# ==================================================
# DELETE /tags
# ==================================================

def test_delete_tags_single(auth, client, db):
    db.query.return_value = []
    res = client.delete('/tags', json={'labels': ['canned']}, headers=auth)
    assert res.status_code == 200
    assert 'canned' in res.get_json()['deleted']


def test_delete_tags_multiple(auth, client, db):
    db.query.return_value = []
    labels = ['canned', 'cereal']
    res = client.delete('/tags', json={'labels': labels}, headers=auth)
    assert res.status_code == 200
    assert set(res.get_json()['deleted']) == set(labels)


def test_delete_tags_empty_list(auth, client):
    res = client.delete('/tags', json={'labels': []}, headers=auth)
    assert res.status_code == 200
    assert res.get_json()['deleted'] == []


def test_delete_tags_missing_labels_field(auth, client):
    res = client.delete('/tags', json={'wrong': []}, headers=auth)
    assert res.status_code == 400




def test_delete_tags_db_error_returns_207(auth, client, db):
    db.query.side_effect = Exception('DB failure')
    res = client.delete('/tags', json={'labels': ['vegan']}, headers=auth)
    assert res.status_code == 207
    assert len(res.get_json()['errors']) == 1


# ==================================================
# GET /products/all/names, /brands, /tags
# ==================================================

def test_get_all_names(auth, client, db, products):
    names = list({p.name for p in products})
    db.all_product_names.return_value = names
    res = client.get('/products/all/names', headers=auth)
    assert res.status_code == 200
    assert set(res.get_json()) == set(names)


def test_get_all_brands(auth, client, db, products):
    brands = list({p.brand for p in products if p.brand})
    db.all_product_brands.return_value = brands
    res = client.get('/products/all/brands', headers=auth)
    assert res.status_code == 200
    assert set(res.get_json()) == set(brands)


def test_get_all_tags(auth, client, db, tag_list):
    labels = [t.label for t in tag_list]
    db.all_product_tags.return_value = labels
    res = client.get('/products/all/tags', headers=auth)
    assert res.status_code == 200
    assert set(res.get_json()) == set(labels)


# ==================================================
# GET /products/available, /names, /brands, /tags
# ==================================================

def test_get_available_products(auth, client, db, inventory):
    # Convert Product objects to dicts for JSON serialization
    db.available_products.return_value = [p.model_dump() for p in inventory]
    res = client.get('/products/available', headers=auth)
    assert res.status_code == 200
    assert len(res.get_json()) == len(inventory)


def test_get_available_names(auth, client, db, inventory):
    names = [p.name for p in inventory]
    db.available_product_names.return_value = names
    res = client.get('/products/available/names', headers=auth)
    assert res.status_code == 200
    assert set(res.get_json()) == set(names)


def test_get_available_brands(auth, client, db, inventory):
    brands = [p.brand for p in inventory if p.brand]
    db.available_product_brands.return_value = brands
    res = client.get('/products/available/brands', headers=auth)
    assert res.status_code == 200
    assert set(res.get_json()) == set(brands)


def test_get_available_tags(auth, client, db, tag_list):
    labels = [t.label for t in tag_list]
    db.available_product_tags.return_value = labels
    res = client.get('/products/available/tags', headers=auth)
    assert res.status_code == 200


# ==================================================
# PATCH /products/checkout
# ==================================================

def test_checkout_valid(auth, client, db, products):
    item = products[4]  # cherrios, quantity=8
    after = Product(id=item.id, name=item.name, brand=item.brand, quantity=5, image_link=None, tags=item.tags)
    db.product_in_table.return_value = item
    db.query.return_value = []
    res = client.patch('/products/checkout', json={'products': [{'id': item.id, 'amount': 3}]}, headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert 'quantities' in data
    assert data['quantities'][0]['id'] == item.id


def test_checkout_last_one(auth, client, db, products):
    item = products[3]  # peas, quantity=2
    db.product_in_table.return_value = item
    db.query.return_value = []
    res = client.patch('/products/checkout', json={'products': [{'id': item.id, 'amount': 2}]}, headers=auth)
    assert res.status_code == 200
    data = res.get_json()
    assert data['quantities'][0]['quantity'] == 0


def test_checkout_not_enough_stock(auth, client, db, products):
    item = products[3]  # peas, quantity=2
    db.product_in_table.return_value = item
    res = client.patch('/products/checkout', json={'products': [{'id': item.id, 'amount': 99}]}, headers=auth)
    assert res.status_code == 400
    assert res.get_json()['error'] == 'not_enough_stock'


def test_checkout_not_found(auth, client, db):
    db.product_in_table.side_effect = ProductNotFoundError('0000')
    res = client.patch('/products/checkout', json={'products': [{'id': '0000', 'amount': 1}]}, headers=auth)
    assert res.status_code == 500




def test_checkout_invalid_schema(auth, client):
    res = client.patch('/products/checkout', json={'products': [{'id': '324'}]}, headers=auth)  # missing amount
    assert res.status_code == 400


def test_checkout_no_auth(client):
    res = client.patch('/products/checkout', json={'products': [{'id': '324', 'amount': 1}]})
    assert res.status_code == 401
