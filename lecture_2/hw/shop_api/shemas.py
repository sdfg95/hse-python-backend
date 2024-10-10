from dataclasses import Field
from typing import Optional

from pydantic import BaseModel, ValidationError, root_validator

from lecture_2.hw.shop_api import Item


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str = None
    price: float = None


class CartCreate(BaseModel):
    pass
