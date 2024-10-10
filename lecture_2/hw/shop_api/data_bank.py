from typing import Dict, List
from lecture_2.hw.shop_api.models import Cart, Item

items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}

item_counter = 1
cart_counter = 1
