import pytest
import sqlite3
from db import add_item, in_table, delete_item, get_tags_for_item


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

#Search test- add items with similar names and return both
#add items with same name dif brand

