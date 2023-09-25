from fastapi import FastAPI, HTTPException, Query, Path
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List
from models.product import Product, Order
from bson import ObjectId
from bson.errors import InvalidId

app = FastAPI()

client = MongoClient("mongodb+srv://bikash:incorrect@cloud.jwcitcy.mongodb.net/")
db = client["ecommerce"]
products_collection: Collection = db["products"]
orders_collection: Collection = db["orders"]

@app.get("/products", response_model=List[Product])
def list_products():
    products = list(products_collection.find())
    get_products = [{"id": str(product["_id"]), **product} for product in products]
    return get_products

@app.post("/products", response_model=Product)
def create_product(product: Product):
    new_product = product.dict()
    product_id = products_collection.insert_one(new_product).inserted_id
    created_product = {**new_product, "id": str(product_id)}
    return created_product

@app.put("/products/{product_id}", response_model=Product, response_model_exclude_unset=True)
def update_product(product_id: str, product: Product):
    # Ensure the provided product_id is a valid ObjectId
    try:
        product_id_obj = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    # Find the product in the database
    existing_product = products_collection.find_one({"_id": product_id_obj})

    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the available quantity
    updated_quantity = product.available_quantity
    products_collection.update_one(
        {"_id": product_id_obj},
        {"$set": {"available_quantity": updated_quantity}}
    )
    # Return the updated product
    updated_product = {**existing_product, "id": product_id, "available_quantity": updated_quantity}
    return updated_product

@app.get("/orders", response_model=List[Order])
def get_orders(skip: int = Query(0, description="Number of records to skip"),
               limit: int = Query(10, description="Number of records to fetch")):
    #skip and limit are non-negative
    if skip < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Skip and limit must be non-negative")

    #Fetch orders from the database with pagination
    orders = list(orders_collection.find().skip(skip).limit(limit))

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str = Path(..., description="Order ID")):
    # Ensure the provided order_id is a valid ObjectId
    try:
        order_id_obj = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    # Find the order in the database by order_id
    order = orders_collection.find_one({"_id": order_id_obj})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=Order)
async def create_order(order: Order):
    new_order = order.dict()
    # Calculate the total amount for order
    total_amount = 0
    for item in order.items:
        try:
            product_id = ObjectId(item.product_id)  # Convert to ObjectId
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid product_id")
        
        product = products_collection.find_one({"_id": product_id})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        total_amount += product["price"] * item.bought_quantity
        # Update the available_quantity of the product
        updated_quantity = product["available_quantity"] - item.bought_quantity
        products_collection.update_one(
            {"_id": product_id},
            {"$set": {"available_quantity": updated_quantity}}
        )
    new_order["total_amount"] = total_amount

    # Insert the order into the MongoDB collection
    order_id = orders_collection.insert_one(new_order).inserted_id
    #Return the order
    created_order = {**new_order, "id": str(order_id)}
    return created_order