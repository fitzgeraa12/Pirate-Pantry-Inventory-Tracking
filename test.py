import db
import sqlite3
#This is where I can test the methods
def main():
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db')
    cursor = connection.cursor()
    print(db.view_table(cursor))
    #print(db.add_item(cursor, 'F', 'W', 234, 100, 'None'))
    db.delete_item(cursor, 39393, True)
    print(db.view_table(cursor))
    print(db.view_pantry_tags(cursor))
    #print(db.add_tags(cursor, ('carbs', 'hfdsal', 'contains nuts')))
    #print(db.view_all_tags(cursor))
    #print(db.get_all_info(cursor, 39393))

    #print(db.get_tags_for_item(cursor, 1234))
    #print(db.view_pantry_tags(cursor))
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()