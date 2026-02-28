import db
import admin
import sqlite3
#This is where I can test the methods
def main():
    connection = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Test_Junction.db')
    cursor = connection.cursor()
    print(db.view_table(cursor))
    #print(db.add_item(cursor, 'F', 'W', 234, 100, 'None'))
    #db.delete_item(cursor, 39393, True)
    #print(db.view_table(cursor))
    #print(db.view_pantry_tags(cursor))
    print(db.update_item(cursor, 'Mystery Soup', 'Campbell\'s', 39393, 5, 'None', 'Beans', 'Bugs', 'Birds', 'Bees')) 
    print(db.checkout_item(cursor, 5555, 10))
    print(db.view_table(cursor))

    #print(db.add_tags(cursor, ('carbs', 'hfdsal', 'contains nuts')))
    #print(db.view_all_tags(cursor))
    #print(db.get_all_info(cursor, 39393)) 
    #print(db.get_tags_for_item(cursor, 39393)) 
    #print(db.view_pantry_tags(cursor))
    cursor.close()
    connection.close()

    """connection2 = sqlite3.connect('/workspaces/Pirate-Pantry-Inventory-Tracking/Admin_Info.db')
    cursor2 = connection2.cursor()
    print(admin.in_table(cursor2, 'james2@southwestern.edu'))
    print(admin.is_admin(cursor2, 'james2@southwestern.edu'))
    print(admin.view_admins(cursor2))
    print(admin.view_trusted(cursor2))
    print(admin.add_user(cursor2, 'trustworthyuser@southwestern.edu', 'admin', 'james2@southwestern.edu'))
    print(admin.view_all(cursor2))
    #print(remove_user(cursor2, 'james2@southwestern.edu'))
    #print(remove_user(cursor2, 'doehlera@southwestern.edu'))
    #print(remove_user(cursor2, 'fitzgeraa@southwestern.edu'))
    #print(remove_user(cursor2, 'trann@southwestern.edu'))
    #print(remove_user(cursor2, 'fakeemail@hotmail.com'))
    print(admin.view_all(cursor2))
    #save(connection2)
    cursor2.close()
    connection2.close()"""

if __name__ == "__main__":
    main()