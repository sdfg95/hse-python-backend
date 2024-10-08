from pydantic import BaseModel, ValidationError, root_validator


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str = None
    price: float = None


class CartCreate(BaseModel):
    pass
