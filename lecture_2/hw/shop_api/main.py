from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Response
from lecture_2.hw.shop_api.models import Cart, Item, CartItem
from lecture_2.hw.shop_api.shemas import ItemCreate, ItemUpdate, CartCreate
from lecture_2.hw.shop_api.data_bank import items_db, carts_db, item_counter, cart_counter

app = FastAPI(title="Shop API")


# Cart
@app.post("/cart", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_cart(response: Response):
    global cart_counter, carts_db

    cart_id = cart_counter
    carts_db[cart_id] = Cart(id=cart_id, items=[], price=0.0)
    cart_counter += 1

    response.headers["Location"] = f"/cart/{cart_id}"

    return {"id": cart_id}


@app.get("/cart/{id}", response_model=Cart)
async def get_cart(id: int):
    cart = carts_db.get(id)
    if cart is None:
        raise HTTPException(status_code=404, detail="No cart in store")
    return cart


@app.get("/cart", response_model=List[Cart])
async def get_all_cart(offset: Optional[int] = 0, limit: Optional[int] = 10,
                       min_price: Optional[float] = None, max_price: Optional[float] = None,
                       min_quantity: Optional[int] = None, max_quantity: Optional[int] = None):
    if offset < 0 or limit < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params")

    if (min_price is not None and min_price < 0) or \
            (max_price is not None and max_price < 0) or \
            (min_quantity is not None and min_quantity < 0) or \
            (max_quantity is not None and max_quantity < 0):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params")

    carts = list(carts_db.values())[offset:offset + limit]

    if min_price is not None:
        carts = [c for c in carts if c.price >= min_price]
    if max_price is not None:
        carts = [c for c in carts if c.price <= max_price]

    if min_quantity is not None:
        carts = [c for c in carts if sum(i.quantity for i in c.items) >= min_quantity]
    if max_quantity is not None:
        carts = [c for c in carts if sum(i.quantity for i in c.items) <= max_quantity]

    return carts


@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_db.get(cart_id)
    item = items_db.get(item_id)

    if not cart or not item or item.deleted:
        raise HTTPException(status_code=404, detail="Cart or item not found or item is deleted")

    existing_item = None
    for i in cart.items:
        if i.id == item_id:
            existing_item = i
            break

    if existing_item:
        existing_item.quantity += 1
    else:
        cart.items.append(CartItem(id=item.id, name=item.name, quantity=1, available=not item.deleted))

    cart.price += item.price
    return cart


@app.post("/item", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global item_counter
    item_id = item_counter
    new_item = Item(id=item_id, name=item.name, price=item.price)
    items_db[item_id] = new_item
    item_counter += 1
    return new_item


@app.get("/item/{id}", response_model=Item)
async def get_item(id: int):
    item = items_db.get(id)
    if item is None or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/item", response_model=List[Item])
async def get_items(
        offset: int = 0,
        limit: int = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        show_deleted: bool = False
):
    if offset < 0 or limit < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params")

    if (min_price is not None and min_price < 0) or \
            (max_price is not None and max_price < 0):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params")

    items = list(items_db.values())

    if min_price is not None:
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price <= max_price]

    if not show_deleted:
        items = [item for item in items if not item.deleted]

    items = items[offset:offset + limit]

    return items


@app.patch("/item/{id}", response_model=Item)
async def update_item(id: int, body: dict):
    item = items_db.get(id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.deleted:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Item is deleted")

    if "deleted" in body or "odd" in body:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query")

    if "name" in body:
        item.name = body["name"]
    if "price" in body:
        item.price = body["price"]

    return item


@app.put("/item/{id}", response_model=Item)
async def update_item(id: int, item: ItemUpdate):
    existing_item = items_db.get(id)
    if existing_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if item.price is None or item.name is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query")
    update_data = item.dict(exclude_unset=True)
    updated_item = existing_item.copy(update=update_data)
    items_db[id] = updated_item

    return updated_item


@app.delete("/item/{id}", status_code=status.HTTP_200_OK)
async def delete_item(id: int):
    item = items_db.get(id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.deleted is True:
        return item

    item.deleted = True
    return item
