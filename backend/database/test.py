import db
import admin

#This is where I can test the methods
def main():
    print(db.view_table())
    #print(db.add_item(cursor, 'F', 'W', 234, 100, 'None'))
    #db.delete_item(cursor, 39393, True)
    #print(db.view_table(cursor))
    #print(db.view_pantry_tags(cursor))
    print(db.update_item('Mystery Soup', 'Campbell\'s', 39393, 5, ['None', 'Beans', 'Bugs', 'Birds', 'Bees'])) 
    print(db.checkout_item(5555, 10))
    print(db.view_table())

    #print(db.add_tags(cursor, ('carbs', 'hfdsal', 'contains nuts')))
    #print(db.view_all_tags())
    #print(db.get_all_info(39393)) 
    #print(db.get_tags_for_item(, 39393)) 
    #print(db.view_pantry_tags())

    #print(admin.in_table(cursor2, 'james2@southwestern.edu'))
    #print(admin.is_admin(cursor2, 'james2@southwestern.edu'))
    #print(admin.view_admins(cursor2))
    #print(admin.view_trusted(cursor2))
    #print(admin.add_user(cursor2, 'trustworthyuser@southwestern.edu', 'admin', 'james2@southwestern.edu'))
    #print(admin.view_all(cursor2))
    #print(remove_user(cursor2, 'james2@southwestern.edu'))
    #print(remove_user(cursor2, 'doehlera@southwestern.edu'))
    #print(remove_user(cursor2, 'fitzgeraa@southwestern.edu'))
    #print(remove_user(cursor2, 'trann@southwestern.edu'))
    #print(remove_user(cursor2, 'fakeemail@hotmail.com'))
    print(admin.view_all())
    print(admin.get_role('james2@southwestern.edu'))
    print(admin.get_role('trustrthyuser@southwestern.edu'))
    print(admin.get_role('fakeemail@hotmail.com'))

if __name__ == "__main__":
    main()