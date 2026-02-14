from backend.sql_alchemy import sql_alchemy

class Product(sql_alchemy.Model):
    def __init__(self, id: int, brand_id: int) -> None:
        self.id: int = id
        self.brand_id: int = brand_id
