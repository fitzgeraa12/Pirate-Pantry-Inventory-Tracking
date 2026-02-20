import sqlite3

#Returns all items with all of their info in the main table
def view_main_table(cursor):
    cursor.execute('SELECT * FROM main_table')
    items = cursor.fetchall()
    #print(items)
    return items

#For each item, returns its ID and all of the tags it's connected to
def view_tags(cursor):
    cursor.execute('SELECT * FROM junction_table') #junction_table is the table that connects items to tags
    tags = cursor.fetchall()
    #print(tags)
    return tags


def main():
    connect = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db')
    cursor = connect.cursor()
    #view_main_table(cursor)
    #view_tags(cursor)
    cursor.close()
    connect.close()

if __name__ == "__main__":
    main()