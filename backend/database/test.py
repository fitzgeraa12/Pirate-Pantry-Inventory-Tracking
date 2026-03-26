import db
import sqlite3
import admin


#This is where I can test the methods
def main():

    
    #Creates the table
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/backend/database/db_test.db')
    cursor = connection.cursor()

    with open('/workspaces/Pirate-Pantry-Inventory-Tracking/backend/migrations/0001_init_schema.sql', 'r') as f:
        schema_script = f.read()
    
    try:
        cursor.executescript(schema_script)
        connection.commit()
    except sqlite3.Error as e:
        print("Oh no!")
    
    #finally:
    
    #cursor.execute('SELECT * FROM products')
    #print(cursor.fetchall())
    #db.add_item('corn', 'HEB', 3835982, 4, 'None', ['VEGETABLES', 'canned'])
    #db.add_item('peas', 'green giant', 324, 2, 'None', ['VEGETABLES', 'canned'])'''
    #db.add_item('carrots', 'HEB', [], 7, 'None', ['VEGETABLES', 'canned'])
    #db.update_item('corn', 'HEB', 3835982, 10, '', ['VEGETABLES', 'canned'])

    #db.delete_item(3835983)
    #print(db.get_tags_for_item(347))
    #db.add_item('olives', 'everyday olives', 345345, 5, 'None', ['VEGETABLES', 'canned'])
    #db.add_item('tomato paste', 'HEB', 4329, 7, 'None', ['VEGETABLES'])
    #db.add_item('diced tomatoes', 'HEB', 49104, 6, 'None', ['VEGETABLES'])
    #db.add_item('roasted tomatoes', 'HEB', 68234, 2, 'None', ['VEGETABLES'])
    #db.add_item('cheerios', 'gereral mills', 48328, 8, 'None', ['cereal'])
    #db.add_item('frosted flakes', 'kellogs', 43453, 1, 'None', ['cereal'])
    #db.add_item('resse\'s puffs', 'general mills', 43824, 3, 'None', ['cereal', 'contains nuts'])
    #db.add_item('deodorant', 'dove', 3994294, 10, 'None', ['toiletries'])
    #db.add_item('deodorant', 'secret', 548239, 5, 'None', ['toiletries'])
    #db.add_item('deodorant', 'under armor', 5729495, 2, 'None', ['toiletries'])
    #db.add_item('corn', 'green giant', 95827, 14, 'None', ['vegetables', 'canned'])
    #db.add_item('pasta', 'HEB', 47283, 5, 'None', ['pasta', 'nut free'])
    #db.add_item('pasta', 'walmart', 1288901, 6, 'None', ['pasta', 'nut free'])
    #db.add_item('pasta', 'HEB', 390438, 8, 'None', ['pasta', 'gluten free'])
    #db.add_item('oatmeal', 'kellogs', 5743843, 2, 'None')
    #db.add_item('oatmeal', 'HEB', 1117362, 15, 'None')
    #db.add_item('liquid soap', 'dove', 3331, 5, 'None', ['soap', 'toiletries'])
    #db.add_item('hand soap', 'soft soap', 4888, 5, 'None', ['soap', 'toiletries'])
    #print(db.view_all_tags())
    #db.add_item('TEST_TOMATO', '', 333333333, 5, '', ['TEST_TAG1','TEST_TAG2',4,'DSAFDSAFDSAFDSA','VegetableS','Canned'])
    #print(db.get_tags_for_item(333333333)) 
    #db.delete_item(333333333)
    #print(admin.view_all())
    print(db.view_table())
   

if __name__ == "__main__":
    main()