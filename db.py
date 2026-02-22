import sqlite3

#Views entire table, including items with quantity 0
def view_table(cursor):
    cursor.execute('SELECT * FROM main_table')
    return cursor.fetchall()

#Returns all items with a quantity > 0 with all of their info in the main table
def view_inventory(cursor):
    cursor.execute('SELECT * FROM main_table WHERE NOT quantity == \'0\'')
    return cursor.fetchall()

#For each item that doesn't have a quantity of 0, returns its ID and all of the tags it's connected to
def view_item_tags(cursor):
    cursor.execute('SELECT id FROM main_table WHERE NOT quantity == \'0\'') #All of the items actually present in the pantry
    ids = [x[0] for x in cursor.fetchall()] #Saves all items to a list
    ids_list = ", ".join(str(t) for t in ids) #Formatting list so SQL can read it
    cursor.execute(f'SELECT * FROM junction_table WHERE id IN ({ids_list})') #junction_table is the table that connects items to tags. 
    return cursor.fetchall()

#Gets all tags, whether they're connected to an item or not
def view_all_tags(cursor):
    cursor.execute('SELECT * FROM tag_table')
    return cursor.fetchall()

#Adds a brand new item to the table. No new tags were created
def add_item(cursor, name, brand, id, quantity, image, tags):
    cursor.execute(f'INSERT INTO main_table VALUES ("{name.title()}", "{brand.title()}", "{id}", "{quantity}", "{image}")') #.title() converts spelling to title case
    for i in tags: #Connects all tags to their item in title table
        cursor.execute(f'INSERT INTO junction_table VALUES ("{id}", "{i.title()}")')
    cursor.execute('SELECT * FROM junction_table')
    return cursor.fetchall()


def main():
    connect = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db')
    cursor = connect.cursor()
    """print(view_table(cursor))
    print(view_inventory(cursor))
    print(view_item_tags(cursor))
    print(view_all_tags(cursor))"""
    print(add_item(cursor, 'potato soUp', 'Campbell\'s', 39393, 9, 'None', ['vegEtaBle', 'CaRbS']))
    print(view_table(cursor))
    cursor.close()
    connect.close()

if __name__ == "__main__":
    main()