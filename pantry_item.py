class PantryItem:
    def __init__(self, id : int, name : str, brand : str, group : str, quantity : int):
        self.id = id
        self.name = name
        self.brand = brand
        self.group = group
        self.quantity = quantity

    def update(self, amount: int):
        if self.quantity + amount < 0:
            self.quantity = 0
        self.quantity += amount