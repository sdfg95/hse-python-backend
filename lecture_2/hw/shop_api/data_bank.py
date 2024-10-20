from typing import Dict, List
from .models import Cart, Item

items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}

item_counter = 1
cart_counter = 1
