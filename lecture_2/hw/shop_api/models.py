from typing import List
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool = True


class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float
