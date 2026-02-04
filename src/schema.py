from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FoodType(db.Model):
    def __init__(self, id: int, brand_id: int) -> None:
        self.id = id
        self.brand_id = brand_id
