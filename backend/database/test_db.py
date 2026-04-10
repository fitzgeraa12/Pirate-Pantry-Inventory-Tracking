import pytest
import sqlite3
from db import add_item, in_table, delete_item, get_tags_for_item, update_item, get_all_info


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
    delete_item(333333333)
    assert in_table(333333333) == False


    #Adding an item with only required fields
    add_item('TEST_ITEM', '', 111111111, 4, '', [])
    assert in_table(111111111) == True
    delete_item(111111111)
    assert in_table(111111111) == False


def test_update():
    add_item('test_update', None, 677777777, 0, '', [])
    assert in_table(677777777) == True
    update_item('test_update', None, 677777777, -1, '', []) == "Invalid quantity"
    update_item('test_update', 'Kroger', 677777777, 5, '', [])
    assert get_all_info(677777777) == [677777777, 'Test_Update', 'Kroger', 5, '']
    
    delete_item(677777777)
    assert in_table(677777777) == False
#Search test- add items with similar names and return both
#add items with same name dif brand

#Test updating item
#test searching item with no id