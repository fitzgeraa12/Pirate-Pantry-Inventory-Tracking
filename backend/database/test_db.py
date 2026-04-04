import pytest
import sqlite3
from db import add_item, in_table, delete_item, get_tags_for_item, update_item, get_all_info, delete_tag, view_pantry_tags


def test_add():
    #Adding an item that already exists
    add_item('TEST_CEREAL', '', 2222222222, 2, '', [])
    assert in_table(2222222222) == True
    assert add_item('TEST_SAME_CEREAL', '',2222222222, 2, '', [] ) == []
    delete_item(2222222222)
    assert in_table(2222222222) == False

    #Adding an item with no id- test ID generation


    #Adding an item with brand new tags
    #Question- should we stop users from adding whitespace/numbers to tags?
    add_item('TEST_APPLE', '', 333333333, 5, '', ['TEST_TAG1','TEST_TAG2', 55, '','Canned', 'red', 'gross fruits'])
    assert get_tags_for_item(333333333) == ['', '55', 'Canned', 'Gross Fruits', 'Red', 'Test_Tag1','Test_Tag2']
    temp = view_pantry_tags()
    all_tags = [x[0] for x in temp]
    assert ('Canned' in all_tags) == True
    delete_item(333333333)
    assert in_table(333333333) == False
    delete_tag('55')
    delete_tag('Canned')
    delete_tag('Gross Fruits')
    delete_tag('Red')
    delete_tag('Test_Tag1')
    delete_tag('Test_Tag2')
    temp = view_pantry_tags()
    all_tags = [x[0] for x in temp]
    assert ('Canned' in all_tags) == False

    

    #Adding an item with only required fields
    add_item('TEST_ITEM', '', 111111111, 4, '', [])
    assert in_table(111111111) == True
    delete_item(111111111)
    assert in_table(111111111) == False


def test_update():
    add_item('test_update', None, 67676767, 0, '', [])
    assert in_table(67676767) == True
    update_item('test_update', None, 67676767, -1, '', []) == "Invalid quantity"
    update_item('test_update', 'Kroger', 67676767, 5, '', [])
    assert get_all_info(67676767) == [67676767, 'Test_Update', 'Kroger', 5, '']
    update_item('test_name_change', None, 67676767, 5, '', ['item_tag'])
    delete_item(67676767)
    assert in_table(67676767) == False
#Search test- add items with similar names and return both
#add items with same name dif brand

#Test updating item
#test searching item with no id