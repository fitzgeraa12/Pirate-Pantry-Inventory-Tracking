from typing import Any, Optional

import requests
import os

# Cloudflare D1 REST API
ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
DATABASE_ID = os.environ.get('CLOUDFLARE_D1_DATABASE_ID')
API_TOKEN = os.environ.get('CLOUDFLARE_D1_API_TOKEN')

API_URL = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DATABASE_ID}/query'

def query(sql: str, params: Optional[list[Any]]= None) -> list[Any]:
    ''' Execute a SQL query against the Cloudflare D1 REST API

        Args:
            sql (str): SQL query to execute
            params (list): Optional list of parameters for the query

        Returns:
            list: Rows returned by the query
    '''
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    body: dict[str, Any] = {'sql': sql}
    if params:
        body['params'] = params

    print(f"TOKEN: '{API_TOKEN}'", flush=True)
    response = requests.post(API_URL, headers=headers, json=body)
    response.raise_for_status()
    data = response.json()

    if not data.get('success'):
        raise Exception(f'D1 query failed: {data.get("errors")}')

    results = data.get('result', [])
    if not results:
        return []

    return results[0].get('results', [])


def rows_to_list(rows: list[Any]) -> list[list[Any]]:
    ''' Convert D1 result dicts to lists for backwards compatibility '''
    return [list(row.values()) for row in rows]


#------------------------------
# Viewing all items in database (including items with quantity 0)
#------------------------------

def view_table():
    rows = query('SELECT * FROM products')
    return rows_to_list(rows)

def view_all_names():
    rows = query('SELECT DISTINCT name FROM products')
    names = [row['name'] for row in rows]
    names.sort()
    return names

def view_all_brands():
    rows = query("SELECT DISTINCT brand FROM products WHERE brand != ''")
    brands = [row['brand'] for row in rows]
    brands.sort()
    return brands

def view_all_tags():
    rows = query('SELECT * FROM tags')
    return rows_to_list(rows)

#------------------------------
# Viewing items currently in the pantry (quantity > 0)
#------------------------------

def view_pantry_inventory():
    rows = query('SELECT * FROM products WHERE quantity > 0')
    return rows_to_list(rows)

def view_pantry_names():
    rows = query('SELECT DISTINCT name FROM products WHERE quantity > 0')
    names = [row['name'] for row in rows]
    names.sort()
    return names

def view_pantry_brands():
    rows = query("SELECT DISTINCT brand FROM products WHERE brand != '' AND quantity > 0")
    brands = [row['brand'] for row in rows]
    brands.sort()
    return brands

def view_pantry_tags():
    rows = query('SELECT DISTINCT tag_label FROM product_tags pt JOIN products p ON pt.product_id = p.id WHERE p.quantity > 0')
    return [row['tag_label'] for row in rows]

#------------------------------
# Updating methods
#------------------------------

def add_item(
        name: str = '',
        brand: str = '',
        id: Optional[int] = None,
        quantity: int = 0,
        image_link: str = '',
        tags: Optional[list[str]] = None
):
    query('INSERT INTO products VALUES (?, ?, ?, ?, ?)', [id, name.title(), brand.title(), quantity, image_link])
    if tags:
        for tag in tags:
            query('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', [tag.title()])
            query('INSERT INTO product_tags VALUES (?, ?)', [id, tag.title()])

def update_item(
        name: str = '',
        brand: str ='',
        id: Optional[int] = None,
        quantity: int = 0,
        tags: Optional[list[str]] = None,
        image_link: str = ''
):
    result = query('SELECT quantity FROM products WHERE id = ?', [id])
    if not result:
        return "Invalid quantity"
    if quantity >= 0:
        old_quantity = result[0]['quantity']
        new_quantity = old_quantity + quantity
        query('UPDATE products SET name = ?, brand = ?, quantity = ?, image_link = ? WHERE id = ?',
              [name.title(), brand.title(), new_quantity, image_link, id])
        if tags:
            for tag in tags:
                query('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', [tag.title()])
                query('INSERT INTO product_tags (product_id, tag_label) VALUES (?, ?) ON CONFLICT (product_id, tag_label) DO NOTHING', [id, tag.title()])
    else:
        return "Invalid quantity"

def checkout_item(id: Optional[int] = None, quantity: int = 0):
    result = query('SELECT quantity FROM products WHERE id = ?', [id])
    if not result:
        return "Invalid quantity"
    old_quantity = result[0]['quantity']
    new_quantity = old_quantity - quantity
    if new_quantity >= 0:
        query('UPDATE products SET quantity = ? WHERE id = ?', [new_quantity, id])
        return new_quantity
    else:
        return "Invalid quantity"

def add_tags_to_table(new_tags: Optional[list[str]] = None):
    if new_tags:
        for tag in new_tags:
            query('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', [tag.title()])

#------------------------------
# Searching the entire table
#------------------------------

def in_table(id: Optional[int] = None):
    result = query('SELECT id FROM products WHERE id = ?', [id])
    return len(result) > 0

def get_all_info(id: Optional[int] = None) -> list[Any]:
    result = query('SELECT * FROM products WHERE id = ?', [id])
    if not result:
        return []
    item = list(result[0].values())
    tags = get_tags_for_item(id=id)
    item.extend(tags)
    return item

#------------------------------
# Searching pantry (items with quantity > 0)
#------------------------------

def search_pantry_by_name(name: str = ''):
    rows = query('SELECT * FROM products WHERE quantity > 0 AND name = ?', [name.title()])
    return rows_to_list(rows)

def search_pantry_by_brand(brand: str = ''):
    rows = query('SELECT * FROM products WHERE quantity > 0 AND brand = ?', [brand.title()])
    return rows_to_list(rows)

def search_pantry_by_id(id: Optional[int] = None):
    rows = query('SELECT * FROM products WHERE quantity > 0 AND id = ?', [id])
    return rows_to_list(rows)

def search_pantry_by_tag(tag: str =''):
    rows = query('''
        SELECT p.* FROM products p
        JOIN product_tags pt ON p.id = pt.product_id
        WHERE p.quantity > 0 AND pt.tag_label = ?
    ''', [tag.title()])
    return rows_to_list(rows)

#------------------------------
# Getting item info
#------------------------------

def get_tags_for_item(id: Optional[int] = None):
    rows = query('SELECT tag_label FROM product_tags WHERE product_id = ?', [id])
    return [row['tag_label'] for row in rows]

def view_image(id: Optional[int] = None) -> Optional[str]:
    rows = query('SELECT image_link FROM products WHERE id = ?', [id])
    if rows:
        return rows[0]['image_link']
    return None

#------------------------------
# Removing methods
#------------------------------

def delete_item(id: Optional[int] = None):
    query('DELETE FROM products WHERE id = ?', [id])
    query('DELETE FROM product_tags WHERE product_id = ?', [id])

def delete_tag(tag: str = ''):
    query('DELETE FROM product_tags WHERE tag_label = ?', [tag])
    query('DELETE FROM tags WHERE label = ?', [tag])
