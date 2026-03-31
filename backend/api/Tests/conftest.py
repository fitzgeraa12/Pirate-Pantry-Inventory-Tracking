import pytest
from backend.api.api import app
from unittest.mock import patch


# https://github.com/ericsalesdeandrade/pytest-fixtures-examples/blob/master/tests/unit/test_calculator_api.py
@pytest.fixture(autouse=True)
def authentication():
    def bypass(*roles):
        def decorator(f):
            return f
        return decorator
  
    with patch("backend.api.auth.requires_roles", bypass), patch("backend.api.api.requires_roles", bypass):
        yield
       
@pytest.fixture
def client():
   app.config['TESTING'] = True
   with app.test_client() as client:
       yield client


@pytest.fixture()
def table():
   return [
       {
           'name':'corn',
           'brand':'HEB',
           'id':3835982,
           'quantity':4,
           'image_link':'None',
           'tags':['VEGETABLES', 'canned']
       },
       {
           'name':'corn',
           'brand':'green giant',
           'id':95827,
           'quantity':14,
           'image_link':'None',
           'tags':['VEGETABLES', 'canned']
       },
       {
           'name':'tomato paste',
           'brand':'HEB',
           'id':4329,
           'quantity':17,
           'image_link':'None',
           'tags':['VEGETABLES']
       },
       {
           'name':'peas',
           'brand':'green giant',
           'id':324,
           'quantity':2,
           'image_link':'None',
           'tags':['VEGETABLES', 'canned']
       },
       {
           'name':'cherrios',
           'brand':'general mills',
           'id':48328,
           'quantity':8,
           'image_link':'None',
           'tags':['cereal']
       },
       {
           'name':'pasta',
           'brand':'walmart',
           'id':1288901,
           'quantity':6,
           'image_link':'None',
           'tags':['pasta', 'nut free']
       },
       {
           'name':'roasted tomatoes',
           'brand':'HEB',
           'id':68234,
           'quantity':0,
           'image_link':'None',
           'tags':['VEGETABLES']
       },
       {
           'name':'oatmeal',
           'brand':'HEB',
           'id':1117362,
           'quantity':0,
           'image_link':'None',
           'tags':[]
       }
   ]


@pytest.fixture()
def tag_list(table):
   # flatten tags
   tag_set = set()
   
   for p in table:
       for tag in p['tags']:
           tag_set.add(tag)
   tags = [t for t in tag_set]
   return tags


@pytest.fixture()
def inventory(table):
   inv = [p for p in table if p['quantity'] > 0]
   return inv

@pytest.fixture()
def empty():
   return []