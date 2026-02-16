# Import create_engine, MetaData
from sqlalchemy import create_engine, MetaData

# Import Table, Column, String, and Integer
from sqlalchemy import Table, Column, String, Integer

from sqlalchemy import select, insert, delete, update

# Define an engine to connect to piratepantry.sqlite: engine (pretend we have one)
engine = create_engine('sqlite:///piratepantry.sqlite')

# Initialize MetaData: metadata
metadata = MetaData()

# Build a census table: census
pantry = Table('Pirate Pantry', metadata,
               Column('id', Integer()),
               Column('name', String(255)),
               Column('brand', String(255)),
               Column('group', String(455)),
               Column('quantity', Integer(), default = 1),
               extend_existing=True)  # redefine or update the table if it already exists in the MetaData

# Create the table in the database
metadata.create_all(engine)


def add_item(id, name, brand, group, quantity=1):
    stmt = insert(pantry).values(id=id, name=name, brand=brand, group=group, quantity=quantity)
    with engine.begin() as connection:
        connection.execute(stmt)


# def update_item():


# def remove_item():