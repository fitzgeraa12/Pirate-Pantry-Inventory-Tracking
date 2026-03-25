
import pytest # pip install pytest
from unittest.mock import patch
from backend.api.api import app
import backend.api.auth as auth


# --------------------------------------------------
# Test GET /products
# --------------------------------------------------


@patch('backend.database.db.query')
def test_get_products_empty(query, client):
   query.return_value = []
   result = client.get('/products')
   assert result.status_code == 200
   assert result.get_json() == []
  
@patch('backend.database.db.query')
def test_get_products(query, client, table):
   query.return_value = table
   result = client.get('/products')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_id(query, client, table):
   query.return_value = [
       p for p in table if p['id'] == 3835982
   ]
   result = client.get('/products?id=3835982')
   assert result.status_code == 200
   assert len(result.get_json()) == 1


@patch('backend.database.db.query')
def test_get_products_by_name(query, client, table):
   query.return_value = [
        p for p in table if p['name'] == 'corn'
   ]
   result = client.get('/products?name=corn')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_contain_name(query, client, table):
   query.return_value = [
        p for p in table if 'or' in p['name']
   ]
   result = client.get('/products?name=*or*')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_start_name(query, client, table):
   query.return_value = [
       p for p in table if p['name'].lower().startswith('co')
   ]
   result = client.get('/products?name=co*')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_end_name(query, client, table):
   query.return_value = [
       p for p in table if p['name'].lower().endswith('orn')
   ]
   result = client.get('/products?name=*orn')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_brand(query, client, table):
   query.return_value = [
       p for p in table if p['brand'] == 'green giant'
   ]
   result = client.get('/products?brand=green+giant')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_contain_brand(query, client, table):
   query.return_value = [
       p for p in table if 'green' in p['brand']
   ]
   result = client.get('/products?brand=*green*')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_start_brand(query, client, table):
   query.return_value = [
       p for p in table if p['brand'].lower().startswith('gree')
   ]
   result = client.get('/products?brand=gree*')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_end_brand(query, client, table):
   query.return_value = [
       p for p in table if p['brand'].lower().endswith('giant')
   ]
   result = client.get('/products?brand=*giant')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_quantity(query, client, table):
   query.return_value = [
       p for p in table if p['quantity'] == 14
   ]
   result = client.get("/products?quantity=14")
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_range_quantity(query, client, table):
   query.return_value = [
       p for p in table if 3 <= p['quantity'] <= 10
   ]
   result = client.get("/products?quantity=3:10")
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_upper_quantity(query, client, table):
   query.return_value = [
       p for p in table if p['quantity'] >= 5
   ]
   result = client.get("/products?quantity=:5")
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_products_by_lower_quantity(query, client, table):
   query.return_value = [
       p for p in table if p['quantity'] <=10
   ]
   result = client.get("/products?quantity=:10")
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_product_by_nonexist_quantity(query, client, table):
   query.return_value = []
   result = client.get("/products?quantity=100")
   assert result.status_code == 200


def test_get_product_by_missing_quantity(client):
   result = client.get("/products?quantity=")
   assert result.status_code == 400


def test_get_products_by_invalid_quantity(client):
   result = client.get("/products?quantity=ten")
   assert result.status_code == 400


def test_get_products_by_empty_range_quantity(client):
   result = client.get("/products?quantity=:")
   assert result.status_code == 400


def test_get_products_by_invalid_range_quantity(client):
   result = client.get('/products?quantity=5:seven')
   assert result.status_code == 400


@patch('backend.database.db.query')
def test_get_products_by_name_and_quantity(query, client, table):
   query.return_value = [
       p for p in table if p['name'] == 'corn' and p['quantity'] <= 10
   ]
   result = client.get('/products?name=corn&quantity=:10')
   assert result.status_code == 200


# @patch('database.db.query')
# def test_get_products_by_image_link(query, client):


@patch('backend.database.db.query')   
def test_get_products_by_tags(query, client, table):
   query.return_value = [
       p for p in table if 'vegetables' in [tag.lower() for tag in p['tags']]
   ]
   result = client.get("/products?tags=vegetables")
   assert result.status_code == 200


# --------------------------------------------------
# Test POST /products
# --------------------------------------------------
@patch("backend.database.db.in_table")
@patch("backend.database.db.query")
def test_post_products_new (query, in_table, client, table):
   in_table.return_value = None
   new = {
           'name':'olives',
           'brand':'everyday olives',
           'id':345345,
           'quantity':5,
           'image':'None',
       }
   assert new not  in table
   table.append(new)
   query.return_value = new
   result = client.post('/products', json=[new])
   assert result.status_code == 201


   data = result.get_json()
   assert 'added' in data
   assert data['errors'] == []
   assert len(data['added']) == 1


@patch("backend.database.db.in_table")
@patch("backend.database.db.get_all_info")
@patch("backend.database.db.query")
def test_post_products_update(query, all_info, in_table, client, table):
   update_info = {
           'name':'sweet peas', # change name from peas to sweet peas
           'brand':'green giant',
           'id':324,
           'quantity':5, # change quantity from 2 to 5
           'image':'None',
           'tags':['VEGETABLES', 'canned']
       }
   existing = [
       p for p in table if p['id'] == update_info['id']
   ]
   in_table.return_value = True
   all_info.return_value = existing
   query.return_value = [update_info]


   result = client.post('/products', json=[update_info])
   assert result.status_code == 201
   # Update table
   for p in table:
       if p['id'] == update_info['id']:
           p.update(update_info)


   data = result.get_json()
   assert 'added' in data
   assert len(data['added']) == 1
   assert data['added'][0]['name'] == 'sweet peas'
   assert data['added'][0]['quantity'] == 5


def test_post_products_not_a_list(client):
   result = client.post("/products", json={"name": "olives"})
   assert result.status_code == 400


   data = result.get_json()
   assert 'errors' in data
   assert len(data['errors']) == 1
   assert len(data['added']) == 0
   assert data['errors'][0]['error'] == 'Expected a list of products'


@patch("backend.database.db.in_table")
def test_post_product_no_name(in_table, client):
   in_table.return_value = False
   no_name = {
           'brand':'walmart',
           'id':1288901,
           'quantity':6,
           'image':'None',
           'tags':['pasta', 'nut free']
       }
   result = client.post("/products", json=[no_name])
   assert result.status_code == 207


   data = result.get_json()
   assert 'errors' in data
   assert len(data['errors']) == 1
   assert len(data['added']) == 0
   assert data['errors'][0]['error'] == 'Name is required for new products'




@patch('backend.database.db.in_table')
@patch('backend.database.db.query')
def test_post_products_with_tags(query, in_table, client, table):
   new = {
       'name': 'liquid soap',
       'brand': 'dove',
       'id': 3331,
       'quantity': 5,
       'image_link': 'None',
       'tags': ['soap', 'toiletries']
   }
   in_table.return_value = False
   query.return_value = [new]
   result = client.post('/products', json=[new])
   assert result.status_code == 201


   # Add to table
   table.append(new)
   data = result.get_json()
   assert len(data['added']) == 1
   assert data['errors'] == []
   assert data['added'][0]['tags'] == ['soap', 'toiletries']


def test_post_products_no_body(client):
   result = client.post('/products', data='', content_type='application/json')
   assert result.status_code == 400


   data = result.get_json()
   assert 'errors' in data
   assert len(data['errors']) == 1
   assert len(data['added']) == 0
   assert data['errors'][0]['error'] == 'Invalid JSON'


@patch('backend.database.db.in_table')
def test_post_products_invalid_name_asterisk(in_table, client):
   a_name = {
           'name': 'pas*ta',
           'brand':'walmart',
           'id':1288901,
           'quantity':6,
           'image':'None',
           'tags':['pasta', 'nut free']
       }
   in_table.return_value = False
   result = client.post('/products', json=[a_name])
  
   data = result.get_json()
   assert len(data['errors']) > 0
   assert data['errors'][0]['error'] == 'name cannot contain *'


@patch('backend.database.db.in_table')
def test_post_products_invalid_name_double_spaces(in_table, client):
   db_name = {
           'name': 'pas  ta',
           'brand':'walmart',
           'id':1288901,
           'quantity':6,
           'image':'None',
           'tags':['pasta', 'nut free']
       }
   in_table.return_value = False
   result = client.post('/products', json=[db_name])
  
   data = result.get_json()
   assert len(data['errors']) > 0
   assert data['errors'][0]['error'] == 'name cannot contain consecutive whitespace'


@patch('backend.database.db.in_table')
def test_post_products_invalid_name_whitespaces(in_table, client):
   ws_name = {
           'name': '  ',
           'brand':'walmart',
           'id':1288901,
           'quantity':6,
           'image':'None',
           'tags':['pasta', 'nut free']
       }
   in_table.return_value = False
   result = client.post('/products', json=[ws_name])
  
   data = result.get_json()
   assert len(data['errors']) > 0
   assert data['errors'][0]['error'] == 'name cannot be whitespace'


@patch('backend.database.db.in_table')
def test_post_products_invalid_tag(in_table, client):
   it_name = {
           'name': 'pasta',
           'brand':'walmart',
           'id':1288901,
           'quantity':6,
           'image':'None',
           'tags':['pas!!!!@ta']
       }
   in_table.return_value = False
   result = client.post('/products', json=[it_name])
  
   data = result.get_json()
   assert len(data['errors']) > 0
   assert data['errors'][0]['error'] == 'name can only contain alphanumeric characters and spaces'


@patch('backend.database.db.in_table')
def test_post_products_quantity_type_error(in_table, client):
   te_tag = {
           'name': 'pasta',
           'brand':'walmart',
           'id':1288901,
           'quantity': 'six',
           'image':'None',
           'tags':['pasta']
       }
   in_table.return_value = False
   result = client.post('/products', json=[te_tag])
   assert len(result.get_json()['errors']) > 0


# --------------------------------------------------
# Test DELETE /products
# --------------------------------------------------
@patch('backend.database.db.delete_item')
def test_delete_products_single_id(delete_item, client, table):
   delete_item.return_value = None
   remove = [
       {
           'name':'corn',
           'brand':'HEB',
           'id':3835982,
           'quantity':4,
           'image':'None',
           'tags':['VEGETABLES', 'canned']
       }
   ]
   result = client.delete('/products', json={'ids': remove['id']})
   assert result.status_code == 200
   data = result.get_json()
   assert remove['id'] in data['deleted']
   assert len(data['deteled']) == 1
   assert data['errors'] == []
   # Remove product from table
   table[:] = [p for p in table if p['id'] != remove['id']]
   assert not any(p['id'] == remove['id'] for p in table)


@patch('backend.database.db.delete_item')
def test_delete_products_multiple(delete_item, client, table):
   delete_item.return_value = None
   del_product = [
       {
           'name':'corn',
           'brand':'green giant',
           'id':95827,
           'quantity':14,
           'image':'None',
           'tags':['VEGETABLES', 'canned']
       },
       {
           'name':'peas',
           'brand':'green giant',
           'id':324,
           'quantity':2,
           'image':'None',
           'tags':['VEGETABLES', 'canned']
       },
       {
           'name':'cherrios',
           'brand':'general mills',
           'id':48328,
           'quantity':8,
           'image':'None',
           'tags':['cereal']
       }
   ]
   ids = []
   for product in del_product:
       ids.append(product['id'])
  
   result = client.delete('/products', json={'ids': ids})
   assert result.status_code == 200
   assert set(result.get_json()['deleted']) == {ids}
   # Remove products from table
   table[:] = [p for p in table if p['id'] not in ids]
   assert not any(p['id'] in ids for p in table)


@patch('backend.database.db.delete_item')
def test_delete_products_empty_list(delete_item, client):
   result = client.delete('/products', json={'ids': []})
   assert result.status_code == 200
   assert result.get_json()['deleted'] == []


# def test_delete_products_missing_ids_field(client):
#     result = client.delete('/products', json={TODO})
#     assert result.status_code == 400


# def test_delete_products_non_integer_ids(client):
#     result = client.delete('/products', json={'ids': ['abc']})
#     assert result.status_code == 400


def test_delete_products_no_body(client):
   result = client.delete('/products', data='', content_type='application/json')
   assert result.status_code == 400
 
   data = result.get_json()
   assert 'errors' in data
   assert len(data['errors']) == 1
   assert len(data['deleted']) == 0
   assert data['errors'][0]['error'] == 'Invalid JSON'


@patch('backend.database.db.delete_item')
def test_delete_products_db_error_returns_207(delete_item, client):
   delete_item.side_effect = Exception('DB error')
   result = client.delete('/products', json={'ids': [000000]})
   assert result.status_code == 207
   assert len(result.get_json()['errors']) == 1


# --------------------------------------------------
# Test GET /tags
# --------------------------------------------------
@patch('backend.database.db.query')
def test_get_tags_all(query, client, tag_list):
   query.return_value = tag_list
   result = client.get('/tags')
   assert result.status_code == 200
   data = result.get_json()
   assert data == tag_list


@patch('backend.database.db.query')
def test_get_tags_empty(query, client):
   query.return_value = []
   result = client.get('/tags')
   assert result.status_code == 200
   assert result.get_json() == []


@patch('backend.database.db.query')
def test_get_tags_exact(query, client, tag_list):
   query.return_value = [{'tags': t} for t in tag_list if t == 'canned']
   result = client.get('/tags?tags=canned')
   assert result.status_code == 200
   assert all(t['tags'] == 'canned' for t in result.get_json())


@patch('backend.database.db.query')
def test_get_tags_contains(query, client, tag_list):
   query.return_value = [
       {'tags': t} for t in tag_list if 'free' in t.lower()
   ]
   result = client.get('/tags?tags=*free*')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_tags_starts_with(query, client, tag_list):
   query.return_value = [
       {'tags': t} for t in tag_list if t.lower().startswith('can')
   ]
   result = client.get('/tags?tags=can*')
   assert result.status_code == 200


@patch('backend.database.db.query')
def test_get_tags_ends_with(query, client):
   query.return_value = [
       {'tags': t} for t in tag_list if t.lower().endswith('free')
   ]
   result = client.get('/tags?tags=*free')
   assert result.status_code == 200


# DEBATE ON IF THIS IS A GOOD EDGE CASE OR NOT
@patch('backend.database.db.query')
def test_get_tags_nonexistent(query, client):
   query.return_value = []
   result = client.get('/tags?tag=nonexistent')
   assert result.status_code == 200
   assert result.get_json() == []


# --------------------------------------------------
# Test POST /tags
# --------------------------------------------------
@patch('backend.database.db.add_tags_to_table')
def test_post_tags_single(add_tags, client, tag_list):
   add_tags.return_value = None
   result = client.post('/tags', json={'tags': ['vegan']})
   assert 'vegan' not in tag_list
   tag_list.append('vegan')
   assert result.status_code == 201
   assert 'vegan' in result.get_json()['added']


@patch('backend.database.db.add_tags_to_table')
def test_post_tags_multiple(add_tags, client, tag_list):
   add_tags.return_value = None
   new = ['toilettries', 'soap', 'gluten free']
   result = client.post('/tags', json={'tags': new})
   for nt in new:
       tag_list.append(nt)
   assert result.status_code == 201
   assert set(result.get_json()['added']) == {'toilettries', 'soap', 'gluten free'}


@patch('backend.database.db.add_tags_to_table')
def test_post_tags_empty_list(add_tags, client):
   result = client.post('/tags', json={'tags': []})
   assert result.status_code == 201
   assert result.get_json()['added'] == []


def test_post_tags_invalid_tags_double_spaces(client):
   result = client.post('/tags', json={'labels': ['dairy  free']})
   assert result.status_code == 207


   data = result.get_json()
   assert len(data['errors']) >= 1
   assert len(data['added']) == 0


def test_post_tags_missing_tags_field(client):
   result = client.post('/tags', json={'wrong': []})
   assert result.status_code == 400
   data = result.get_json()
   assert len(data['errors']) >= 1
   assert len(data['added']) == 0


def test_post_tags_no_body(client):
   result = client.post('/tags', data='', content_type='application/json')
   assert result.status_code == 400


   data = result.get_json()
   assert 'errors' in data
   assert len(data['errors']) >= 1
   assert len(data['added']) == 0
   assert data['errors'][0]['error'] == 'Invalid JSON'


@patch('backend.database.db.add_tags_to_table')
def test_post_tags_db_error_returns_207(add_tags, client):
   add_tags.side_effect = Exception('DB failure')
   result = client.post('/tags', json={'labels': ['vegan']})
   assert result.status_code == 207
   assert len(result.get_json()['errors']) == 1


# --------------------------------------------------
# Test DELETE /tags
# --------------------------------------------------
@patch('backend.database.db.delete_tag')
def test_delete_tags_single(delete_tag, client, tag_list):
   delete_tag.return_value = None
   result = client.delete('/tags', json={'tags': ['vegan']})
   assert result.status_code == 200
   assert 'vegan' in result.get_json()['deleted']
   # Remove tags from tag_list
   tag_list[:] = [t for t in tag_list if t != 'vegan']
   assert 'vegan' not in tag_list


@patch('backend.database.db.delete_tag')
def test_delete_tags_multiple(delete_tag, client, tag_list):
   delete_tag.return_value = None
   tags_to_delete = ['canned', 'cereal']
   result = client.delete('/tags', json={'tags': tags_to_delete})
   assert result.status_code == 200
   assert set(result.get_json()['deleted']) == {'canned', 'cereal'}
   # Remove tags from tag_list
   tag_list[:] = [t for t in tag_list if t not in tags_to_delete]
   assert not any(t in tag_list for t in tags_to_delete)


@patch('backend.database.db.delete_tag')
def test_delete_tags_empty_list(client):
   result = client.delete('/tags', json={'tags': []})
   assert result.status_code == 207
   data = result.get_json()
   assert data['deleted'] == []
   assert len(data['errors']) > 0


def test_delete_tags_missing_tags_field(client):
   result = client.delete('/tags', json={'wrong': []})
   assert result.status_code == 400


def test_delete_tags_no_body(client):
   result = client.delete('/tags', data='', content_type='application/json')
   assert result.status_code == 400


   data = result.get_json()
   assert 'errors' in data
   assert len(data['errors']) >= 1
   assert len(data['added']) == 0
   assert data['errors'][0]['error'] == 'Invalid JSON'


@patch('backend.database.db.delete_tag')
def test_delete_tags_db_error_returns_207(delete_tag, client):
   delete_tag.side_effect = Exception('DB failure')
   result = client.delete('/tags', json={'tags': ['vegan']})
   assert result.status_code == 207
   assert len(result.get_json()['errors']) == 1
  
# --------------------------------------------------
# Test GET /tables
# --------------------------------------------------
@patch('backend.database.db.view_table')
def test_get_table(view_table, client, table):
   view_table.return_value = table
   result = client.get('/table')
   assert result.status_code == 200
   assert len(result.get_json()) == len(table)


@patch('backend.database.db.view_table')
def test_get_table_empty(view_table, client):
   view_table.return_value = []
   result = client.get('/table')
   assert result.status_code == 200
   assert result.get_json() == []


@patch('backend.database.db.view_all_names')
def test_get_all_names(view_all_names, client, table):
   names = list({p['name'] for p in table})
   view_all_names.return_value = names
   result = client.get('/table/all_names')
   assert result.status_code == 200
   assert names in result.get_json()


@patch('backend.database.db.view_all_brands')
def test_get_all_brands(view_all_brands, client, table):
   brands = list({p['brand'] for p in table})
   view_all_brands.return_value = brands
   result = client.get('/table/all_brands')
   assert result.status_code == 200
   assert brands in result.get_json()


@patch('backend.database.db.view_all_tags')
def test_get_all_tags(view_all_tags, client, tag_list):
   view_all_tags.return_value = tag_list
   result = client.get('/table/all_tags')
   assert result.status_code == 200
   assert tag_list in result.get_json()


# --------------------------------------------------
# Test GET /inventory
# --------------------------------------------------
@patch('backend.database.db.view_pantry_inventory')
def test_get_inventory(view_pantry_inventory, client, inventory):
   view_pantry_inventory.return_value = inventory
   result = client.get('/inventory')
   assert result.status_code == 200
   assert len(result.get_json()) == len(inventory)


@patch('backend.database.db.view_pantry_inventory')
def test_get_inventory_empty(view_pantry_inventory, client):
   view_pantry_inventory.return_value = []
   result = client.get('/inventory')
   assert result.status_code == 200
   assert result.get_json() == []


@patch('backend.database.db.view_pantry_names')
def test_get_inventory_names(view_pantry_names, client, inventory):
   names = [i['name'] for i in inventory]
   view_pantry_names.return_value = names
   result = client.get('/inventory/names')
   assert result.status_code == 200
   assert names in result.get_json()


@patch('backend.database.db.view_pantry_brands')
def test_get_inventory_brands(view_pantry_brands, client, inventory):
   brands = [i['brand'] for i in inventory]
   view_pantry_brands.return_value = brands
   result = client.get('/inventory/brands')
   assert result.status_code == 200
   assert brands in result.get_json()


@patch('backend.database.db.view_pantry_tags')
def test_get_inventory_tags(view_pantry_tags, client, tag_list):
   view_pantry_tags.return_value = tag_list
   result = client.get('/inventory/tags')
   assert result.status_code == 200
   assert tag_list in result.get_json()


# --------------------------------------------------
# Test PATCH /inventory/checkout/<id>
# --------------------------------------------------
@patch('backend.database.db.checkout_item')
@patch('backend.database.db.in_table')
def test_checkout_item_valid(in_table, checkout_item, client, table):
   item = [
       {
           'name':'cherrios',
           'brand':'general mills',
           'id':48328,
           'quantity':8,
           'image_link':'None',
           'tags':['cereal']
       }]
   in_table.return_value = [
       p for p in table if p['id'] == item['id']
   ]
   checkout_item.return_value = 5
   result = client.patch('/inventory/checkout/48328', json={'quantity': 3})
   assert result.status_code == 200


   data = result.get_json()
   assert data['new_quantity'] == 5
   assert data['message'] == 'Item checked out!'
   # Change quantity in table
   for p in table:
       if p['id'] == item['id']:
           p['quantity'] = data['new_quantity']


@patch('backend.database.db.checkout_item')
@patch('backend.database.db.in_table')
def test_checkout_item_last_one(in_table, checkout_item, client, table):
   item = [
       {
           'name':'peas',
           'brand':'green giant',
           'id':324,
           'quantity':2,
           'image_link':'None',
           'tags':['VEGETABLES', 'canned']
       }
   ]
   in_table.return_value = [
       p for p in table if p['id'] == item['id']
   ]
   checkout_item.return_value = 0
   result = client.patch('/inventory/checkout/324', json={'quantity': 2})
   assert result.status_code == 200


   data = result.get_json()
   assert data['new_quantity'] == 0
   assert data['message'] == 'Item checked out!'
   # Change quantity in table
   for p in table:
       if p['id'] == item['id']:
           p['quantity'] = data['new_quantity']


@patch('backend.database.db.in_table')
def test_checkout_item_not_found(in_table, client):
   in_table.return_value = False
   result = client.patch('/inventory/checkout/0000', json={'quantity': 1})
   assert result.status_code == 404
   assert result.get_json()['error'][0] == 'Item not found'


@patch('backend.database.db.checkout_item')
@patch('backend.database.db.in_table')
def test_checkout_item_negative_result(in_table, checkout_item, client, table):
   item = {
           'name':'peas',
           'brand':'green giant',
           'id':324,
           'quantity':2,
           'image_link':'None',
           'tags':['VEGETABLES', 'canned']
       }
   in_table.return_value = [p for p in table if p['id'] == item['id']]
   checkout_item.return_value = 'Invalid quantity'
   result = client.patch('/inventory/checkout/324', json={'quantity': 99})
   assert result.status_code == 400
   assert result.get_json()['error'][0] == 'New quantity can\'t be negative'


def test_checkout_item_zero_quantity(client):
   result = client.patch('/inventory/checkout/324', json={'quantity': 0})
   assert result.status_code == 400
   assert result.get_json()['error'][0] == 'Checkout quantity must be above 0'


def test_checkout_item_negative_quantity(client):
   result = client.patch('/inventory/checkout/324', json={'quantity': -3})
   assert result.status_code == 400
   assert result.get_json()['error'][0] == 'Checkout quantity must be above 0'


def test_checkout_item_nonint_quantity(client):
   result = client.patch('/inventory/checkout/324', json={'quantity': 1.5})
   assert result.status_code == 400
   assert result.get_json()['error'][0] == 'Quantity must be an integer'


def test_checkout_item_str_quantity(client):
   result = client.patch('/inventory/checkout/324', json={'quantity': 'two'})
   assert result.status_code == 400
   assert result.get_json()['error'][0] == 'Quantity must be an integer'


def test_checkout_item_missing_quantity(client):
   result = client.patch('/inventory/checkout/324', json={})
   assert result.status_code == 400
   assert result.get_json()['error'][0] == 'Missing required field: quantity'


def test_checkout_item_no_body(client):
   result = client.patch('/inventory/checkout/324', data='', content_type='application/json')
   assert result.status_code == 400
   assert result.get_json()['error'][0] == 'Invalid JSON'


# --------------------------------------------------
# Test GET /inventory/search/*
# --------------------------------------------------


@patch('backend.database.db.search_pantry_by_name')
def test_search_by_name(search_pantry_by_name, client, inventory):
   search_pantry_by_name.return_value = [
       p for p in table if p['name'] == 'corn'
   ]
   result = client.get('/inventory/search/name/corn')
   assert result.status_code == 200
   assert all(p['name'] == 'corn' for p in result.get_json())


@patch('backend.database.db.search_pantry_by_name')
def test_search_by_name_not_found(search_pantry_by_name, client):
   search_pantry_by_name.return_value = []
   result = client.get('/inventory/search/name/nonexistent')
   assert result.status_code == 200
   assert result.get_json() == []


@patch('backend.database.db.search_pantry_by_brand')
def test_search_by_brand(search_pantry_by_brand, client, inventory):
   search_pantry_by_brand.return_value = [
       p for p in inventory if p['brand'] == 'HEB'
   ]
   result = client.get('/inventory/search/brand/HEB')
   assert result.status_code == 200
   assert all(p['brand'] == 'HEB' for p in result.get_json())


@patch('backend.database.db.search_pantry_by_brand')
def test_search_by_brand_not_found(search_pantry_by_brand, client):
   search_pantry_by_brand.return_value = []
   result = client.get('/inventory/search/brand/Gucci')
   assert result.status_code == 200
   assert result.get_json() == []


@patch('backend.database.db.search_pantry_by_id')
def test_search_by_id(search_pantry_by_id, client, inventory):
   item = [
       {
           'name':'tomato paste',
           'brand':'HEB',
           'id':4329,
           'quantity':17,
           'image_link':'None',
           'tags':['VEGETABLES']
       }
   ]
   search_pantry_by_id.return_value = [
       p for p in inventory if p['id'] == item['id']
   ]
   result = client.get('/inventory/search/id/4329')
   assert result.status_code == 200
   assert result.get_json()[0]['id'] == item['id']


@patch('backend.database.db.search_pantry_by_id')
def test_search_by_id_not_found(search_pantry_by_id, client):
   search_pantry_by_id.return_value = []
   result = client.get('/inventory/search/id/0000')
   assert result.status_code == 200
   assert result.get_json() == []


@patch('backend.database.db.search_pantry_by_tag')
def test_search_by_tag(search_pantry_by_tag, client, inventory):
   search_pantry_by_tag.return_value = [
       p for p in inventory if 'canned' in p['tags']
   ]
   result = client.get('/inventory/search/tags/canned')
   assert result.status_code == 200
   assert all('canned' in p['tags'] for p in result.get_json())


@patch('backend.database.db.search_pantry_by_tag')
def test_search_by_tag_not_found(search_pantry_by_tag, client):
   search_pantry_by_tag.return_value = []
   result = client.get('/inventory/search/tags/nonexistent')
   assert result.status_code == 200
   assert result.get_json() == []


@patch('backend.database.db.search_pantry_by_tag')
def test_search_by_tag_multiple(search_pantry_by_tag, client, inventory):
   tags = ['VEGETABLES', 'canned']
   for t in tags:
       search_pantry_by_tag.return_value = [
           i for i in inventory if t in i['tags']
       ]
   result = client.get('/inventory/search/tags?tags=vegetables,canned')
   assert result.status_code == 200
   for t in tags:
       assert all(t in i['tags'] for i in result.get_json())
