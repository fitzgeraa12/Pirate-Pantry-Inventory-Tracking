from typing import Any, Optional

from dotenv import load_dotenv, dotenv_values #Loads info as env variables or a dictionary

import sqlite3

import requests
import os


load_dotenv()


# Cloudflare D1 REST API
ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID') #Returning none
DATABASE_ID = os.environ.get('CLOUDFLARE_D1_DATABASE_ID')
API_TOKEN = os.environ.get('CLOUDFLARE_D1_API_TOKEN')


API_URL = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DATABASE_ID}/query'

def query(sql: str, params: Optional[list[Any]]= None) -> list[Any]:
    ''' Execute a SQL query against the Cloudflare D1 REST API
        Commented out until Cloudflare stuff is sorted out. Using local tables

        Args:
            sql (str): SQL query to execute
            params (list): Optional list of parameters for the query

        Returns:
            list: Rows returned by the query
    ''
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
    '''
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/backend/database/db_test.db')
    cursor_t = connection.cursor()
    if params:
        cursor_t.execute(sql, params)
        #print(sql, params)
    else:
        cursor_t.execute(sql)
    #results = data.get('result', [])
    results = cursor_t.fetchall()
    connection.commit()
    connection.close()
    if not results:
        return []

    
    return results #results[0].get('results', [])

def rows_to_list(rows: list[Any]) -> list[list[Any]]:
    ''' Convert D1 result dicts to lists for backwards compatibility '''
    return [list(row.values()) for row in rows]


#------------------------------
# Viewing all items in database (including items with quantity 0)
#------------------------------

def view_table():
    rows = query('SELECT * FROM products')
    return rows

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
    return rows

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
        brand: Optional[str] = None,
        id: Optional[int] = None,
        quantity: int = 0,
        image_link: str = '',
        tags: Optional[list[str]] = None
):
    '''Adds brand new item to the table.
        Returns [] if id is already in the table'''

    if brand is not None:
        brand = brand.title()
    if id:
        if in_table(id): #TODO: Should this call update_item instead?
            return []
        else:
            query('INSERT INTO products VALUES (?, ?, ?, ?, ?)', [id, name.title(), brand, quantity, image_link])
    else: #TODO: id autoincrements from last entered id- how close are ID values to each other? Will this be an issue?
        new_id = in_table_no_id(name, brand)
        if len(new_id) > 0: #Item is already in the table
            id = new_id[0][0]
            update_item(name, brand, id, quantity, image_link, None)
        else: #Item is not in table, generate new id
            new_id = [x[0] for x in query('INSERT INTO products VALUES (Null, ?, ?, ?, ?) RETURNING id', [name.title(), brand, quantity, image_link])]
            id = new_id[0]
    if tags:
        for tag in tags:
            query('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', [str(tag).title()])
            query('INSERT INTO product_tags VALUES (?, ?) ON CONFLICT (product_id, tag_label) DO NOTHING', [id, str(tag).title()])

#TODO: How exact should this search be? What if an item is entered manually with no brand, but it already exists in the database with the brand field?
def in_table_no_id(
        name: str = '',
        brand: Optional[str] = None,
):
    '''Searches for the item in the table if there's no id attatched to it (maunal entry)'''
    if brand is None:
        brand = ''
    else:
        brand = brand.title() 
    result = build_query('SELECT id FROM products WHERE ', '', name.title(), brand.title(), [], -1, None, True) 
    result = query(result[0], result[1])
    return result 


def build_query(
        start: str = '',
        end: str = '',
        name: str = '',
        brand: Optional[str] = None,
        id: list[int] = None,
        quantity: int = -1,
        image_link: str = None,
        ands: bool = False
    ):
    '''Builds a query with desired parameters'''
    new_query = []
    conds = []
    if id:
        new_query.append("id = ?")
        conds.append(id)
    if name:
        new_query.append("name = ?")
        conds.append(name.title())
    if brand:
        new_query.append("brand = ?")
        conds.append(brand.title())
    if quantity > 0:
        new_query.append("quantity = ?")
        conds.append(quantity)
    if image_link:
        new_query.append("image_link = ?")
        conds.append(image_link)
    joined_query = ", ".join(new_query)
    if ands:
        and_query = joined_query.replace(", ", " AND ")
        if and_query:
            final = start + and_query + end
            return final, conds
    if joined_query:
        final = start + joined_query + end
        return final, conds

def update_item(
        name: str = '',
        brand: Optional[str] = None,
        id: list[int] = None,
        quantity: int = 0,
        image_link: Optional[str] = None,
        tags: Optional[list[str]] = None
):
    '''Updates information for an item. Adds new quantity to existing quantity'''
    current_quantity = query('SELECT quantity FROM products WHERE id = ?', [id])
    if not current_quantity:
        return "Item not found"
    if quantity >= 0:
        new_quantity = current_quantity[0][0] + quantity
        result = build_query('UPDATE products SET ', ' WHERE id = ?', name, brand, None, new_quantity, image_link, False)
        conds = result[1]
        conds.append(id)
        query(result[0], conds) 
        if tags:
            for tag in tags:
                query('INSERT INTO tags (label) VALUES (?) ON CONFLICT (label) DO NOTHING', [tag.title()])
                query('INSERT INTO product_tags (product_id, tag_label) VALUES (?, ?) ON CONFLICT (product_id, tag_label) DO NOTHING', [id, tag.title()])
    else:
        return "Invalid quantity"

def search(val: str):
    '''Returns ids for all items who's name, brand, or tags contain val. Returns empty set if no match was found'''
    #TODO: Should this return item info?
    searching = '%' + val + '%'
    found = set()
    name_search = query('SELECT id FROM products WHERE name LIKE ?', [searching])
    if len(name_search) > 0:
        name_ids = [x[0] for x in name_search]
        for i in name_ids:
            found.add(i)
    brand_search = query('SELECT id FROM products WHERE brand LIKE ?', [searching])
    if len(brand_search) > 0:
        brand_ids = [x[0] for x in brand_search]
        for i in brand_ids:
            found.add(i)
    tag_search = get_tagged_items([val])
    if len(tag_search) > 0:
        tagged_ids = [x[0] for x in tag_search]
        for i in tagged_ids:
            found.add(i)
    if len(found) > 0:
        return found
    return {}


def checkout_item(id: Optional[int] = None, quantity: int = 0):
    result = query('SELECT quantity FROM products WHERE id = ?', [id])
    if not result:
        return "Invalid quantity"
    old_quantity = result[0][0]
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
    item = list(result[0])
    tags = get_tags_for_item(id=id)
    item.extend(tags)
    return item

#------------------------------
# Searching pantry (items with quantity > 0). TODO: Do I replace these with general search?
#------------------------------

def search_pantry_by_name(name: str = ''):
    rows = query('SELECT * FROM products WHERE quantity > 0 AND name LIKE = ?', [name.title()])
    return rows_to_list(rows)

def search_pantry_by_brand(brand: str = ''):
    rows = query('SELECT * FROM products WHERE quantity > 0 AND brand LIKE = ?', [brand.title()])
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
    return [x[0] for x in rows]

def view_image(id: Optional[int] = None) -> Optional[str]:
    rows = query('SELECT image_link FROM products WHERE id = ?', [id])
    if rows:
        return rows[0]['image_link']
    return None

def get_tagged_items(
        
        tags: Optional[list[str]] = None
        ):
    ids = set()
    for i in tags:
        searching = '%' + i + '%'
        result = query('SELECT product_id FROM product_tags WHERE tag_label LIKE ?', [searching])
        if len(result) > 0:
            temp_list = [x[0] for x in result]
            for j in temp_list:
                ids.add(j)
    items = []
    for k in ids:
        product = query('SELECT * FROM products WHERE id = ?', [k])
        items.append(list(product[0]))
    return items  

#------------------------------
# Removing methods
#------------------------------

def delete_item(id: Optional[int] = None):
    query('DELETE FROM products WHERE id = ?', [id])
    query('DELETE FROM product_tags WHERE product_id = ?', [id])

def delete_tag(tag: str = ''):
    query('DELETE FROM product_tags WHERE tag_label = ?', [tag])
    query('DELETE FROM tags WHERE label = ?', [tag])

#------------------------------
# Auth
#------------------------------

def cache_auth(token: str) -> bool:
    result = query('INSERT INTO auth_cache (token) VALUES (?) ON CONFLICT (token) DO NOTHING RETURNING token', [token])
    return len(result) > 0
